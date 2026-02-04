from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Fundraiser, Donation, User
from datetime import datetime

fundraisers_bp = Blueprint('fundraisers', __name__)

@fundraisers_bp.route('/', methods=['POST'])
@jwt_required()
def create_fundraiser():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check subscription
        if user.subscription_plan == 'free':
            return jsonify({'error': 'Free users cannot create fundraisers. Upgrade to Standard or Premium.'}), 403
        
        data = request.get_json()
        
        required_fields = ['title', 'description', 'target_amount', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Parse end date
        try:
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
        
        if end_date <= datetime.utcnow():
            return jsonify({'error': 'End date must be in the future'}), 400
        
        # Create fundraiser
        fundraiser = Fundraiser(
            user_id=current_user_id,
            memorial_id=data.get('memorial_id'),
            title=data['title'],
            description=data['description'],
            target_amount=float(data['target_amount']),
            end_date=end_date,
            currency=data.get('currency', 'KES'),
            cover_image=data.get('cover_image'),
            status='active'
        )
        
        db.session.add(fundraiser)
        db.session.commit()
        
        return jsonify({
            'message': 'Fundraiser created successfully',
            'fundraiser': fundraiser.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fundraisers_bp.route('/', methods=['GET'])
def get_fundraisers():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', 'active')
        
        query = Fundraiser.query
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        query = query.filter_by(is_verified=True)
        
        fundraisers = query.order_by(Fundraiser.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'fundraisers': [fundraiser.to_dict() for fundraiser in fundraisers.items],
            'total': fundraisers.total,
            'pages': fundraisers.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fundraisers_bp.route('/<fundraiser_id>', methods=['GET'])
def get_fundraiser(fundraiser_id):
    try:
        fundraiser = Fundraiser.query.get(fundraiser_id)
        
        if not fundraiser:
            return jsonify({'error': 'Fundraiser not found'}), 404
        
        # Get recent donations
        donations = Donation.query.filter_by(fundraiser_id=fundraiser_id)\
            .order_by(Donation.created_at.desc())\
            .limit(10)\
            .all()
        
        fundraiser_data = fundraiser.to_dict()
        fundraiser_data['recent_donations'] = [donation.to_dict() for donation in donations]
        
        return jsonify(fundraiser_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fundraisers_bp.route('/<fundraiser_id>/donate', methods=['POST'])
def donate(fundraiser_id):
    try:
        fundraiser = Fundraiser.query.get(fundraiser_id)
        
        if not fundraiser:
            return jsonify({'error': 'Fundraiser not found'}), 404
        
        if fundraiser.status != 'active':
            return jsonify({'error': 'This fundraiser is not accepting donations'}), 400
        
        data = request.get_json()
        
        required_fields = ['amount', 'donor_name', 'donor_phone', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        
        # Generate transaction ID
        transaction_id = f"TXN{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
        
        donation = Donation(
            fundraiser_id=fundraiser_id,
            donor_id=current_user_id,
            amount=float(data['amount']),
            payment_method=data['payment_method'],
            transaction_id=transaction_id,
            donor_name=data['donor_name'],
            donor_email=data.get('donor_email'),
            donor_phone=data['donor_phone'],
            message=data.get('message'),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        # Update fundraiser total
        fundraiser.current_amount += float(data['amount'])
        
        # Check if target reached
        if fundraiser.current_amount >= fundraiser.target_amount:
            fundraiser.status = 'completed'
        
        db.session.add(donation)
        db.session.commit()
        
        return jsonify({
            'message': 'Donation recorded successfully',
            'donation': donation.to_dict(),
            'transaction_id': transaction_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fundraisers_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_fundraisers():
    try:
        current_user_id = get_jwt_identity()
        
        fundraisers = Fundraiser.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'fundraisers': [fundraiser.to_dict() for fundraiser in fundraisers],
            'count': len(fundraisers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
