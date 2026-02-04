from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import requests
import base64
from datetime import datetime
from app import db
from app.models import Payment, User
from app.config import Config

payments_bp = Blueprint('payments', __name__)

# Initialize Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

class MpesaService:
    def __init__(self):
        self.consumer_key = Config.MPESA_CONSUMER_KEY
        self.consumer_secret = Config.MPESA_CONSUMER_SECRET
        self.shortcode = Config.MPESA_SHORTCODE
        self.passkey = Config.MPESA_PASSKEY
        self.callback_url = Config.MPESA_CALLBACK_URL
    
    def get_access_token(self):
        """Get M-Pesa access token"""
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {'Authorization': f'Basic {encoded_auth}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            raise Exception(f"M-Pesa token error: {str(e)}")
    
    def stk_push(self, phone, amount, reference, description):
        """Initiate STK Push"""
        token = self.get_access_token()
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{self.shortcode}{self.passkey}{timestamp}".encode()
        ).decode()
        
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": reference,
            "TransactionDesc": description
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"M-Pesa STK Push error: {str(e)}")

mpesa_service = MpesaService()

@payments_bp.route('/mpesa', methods=['POST'])
@jwt_required()
def initiate_mpesa_payment():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        required_fields = ['amount', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        amount = float(data['amount'])
        phone = data['phone']
        
        # Format phone number (ensure it starts with 254)
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
        
        # Create payment record
        payment = Payment(
            user_id=current_user_id,
            amount=amount,
            payment_method='mpesa',
            status='pending',
            description=data.get('description', 'KENFUSE Payment')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Initiate M-Pesa payment
        reference = f"KENFUSE{payment.id[:8].upper()}"
        description = data.get('description', 'KENFUSE Service Payment')
        
        mpesa_response = mpesa_service.stk_push(
            phone=phone,
            amount=int(amount),
            reference=reference,
            description=description
        )
        
        # Update payment with M-Pesa response
        if mpesa_response.get('ResponseCode') == '0':
            payment.payment_data = mpesa_response
            payment.transaction_id = mpesa_response.get('CheckoutRequestID')
            db.session.commit()
            
            return jsonify({
                'message': 'M-Pesa payment initiated successfully',
                'payment': payment.to_dict(),
                'checkout_request_id': mpesa_response.get('CheckoutRequestID')
            }), 200
        else:
            payment.status = 'failed'
            db.session.commit()
            
            return jsonify({
                'error': 'M-Pesa payment failed',
                'details': mpesa_response
            }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/card', methods=['POST'])
@jwt_required()
def create_card_payment():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'amount' not in data:
            return jsonify({'error': 'Amount required'}), 400
        
        amount = float(data['amount'])
        
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='kes',
            metadata={
                'user_id': current_user_id,
                'description': data.get('description', 'KENFUSE Payment')
            }
        )
        
        # Create payment record
        payment = Payment(
            user_id=current_user_id,
            amount=amount,
            payment_method='card',
            status='pending',
            stripe_payment_intent=intent.id,
            description=data.get('description', 'KENFUSE Payment')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Card payment initiated',
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    try:
        data = request.get_json()
        
        # Process M-Pesa callback
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        
        # Find payment by checkout request ID
        payment = Payment.query.filter_by(transaction_id=checkout_request_id).first()
        
        if payment:
            if result_code == 0:
                payment.status = 'completed'
                # Extract M-Pesa receipt number
                callback_metadata = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.mpesa_receipt = item.get('Value')
                        break
            else:
                payment.status = 'failed'
            
            payment.payment_data = data
            db.session.commit()
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/subscription/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'plan' not in data:
            return jsonify({'error': 'Plan required'}), 400
        
        plan = data['plan']
        
        if plan not in ['free', 'standard', 'premium']:
            return jsonify({'error': 'Invalid plan'}), 400
        
        # Get plan price from config
        from app.config import Config
        plan_price = Config.SUBSCRIPTION_PLANS[plan]['price']
        
        # If free plan, just update
        if plan_price == 0:
            user.subscription_plan = plan
            db.session.commit()
            
            return jsonify({
                'message': f'Subscription updated to {plan}',
                'user': user.to_dict()
            }), 200
        
        # For paid plans, require payment
        if 'payment_method' not in data:
            return jsonify({'error': 'Payment required for paid plans'}), 400
        
        payment_method = data['payment_method']
        
        if payment_method == 'mpesa':
            if 'phone' not in data:
                return jsonify({'error': 'Phone number required for M-Pesa'}), 400
            
            # Process M-Pesa payment
            payment_response = mpesa_service.stk_push(
                phone=data['phone'],
                amount=plan_price,
                reference=f"SUB{user.id[:8]}",
                description=f"KENFUSE {plan.capitalize()} Subscription"
            )
            
            if payment_response.get('ResponseCode') == '0':
                user.subscription_plan = plan
                db.session.commit()
                
                return jsonify({
                    'message': f'Subscription upgraded to {plan}',
                    'user': user.to_dict()
                }), 200
            else:
                return jsonify({
                    'error': 'Payment failed',
                    'details': payment_response
                }), 400
        
        elif payment_method == 'card':
            # For card payments, return payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(plan_price * 100),
                currency='kes',
                metadata={
                    'user_id': current_user_id,
                    'plan': plan,
                    'type': 'subscription'
                }
            )
            
            return jsonify({
                'message': 'Payment required',
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'plan': plan,
                'amount': plan_price
            }), 200
        
        else:
            return jsonify({'error': 'Invalid payment method'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
