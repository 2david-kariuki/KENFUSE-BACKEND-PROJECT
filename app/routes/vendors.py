from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import VendorProfile, VendorService, User

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/register', methods=['POST'])
@jwt_required()
def register_vendor():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check subscription
        if user.subscription_plan != 'premium':
            return jsonify({'error': 'Premium subscription required for vendor marketplace'}), 403
        
        # Check if already a vendor
        if user.role == 'vendor' or VendorProfile.query.filter_by(user_id=current_user_id).first():
            return jsonify({'error': 'User is already registered as a vendor'}), 409
        
        data = request.get_json()
        
        required_fields = [
            'business_name', 'business_registration', 'category',
            'description', 'years_in_operation', 'county', 'town',
            'address', 'phone', 'email'
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Update user role
        user.role = 'vendor'
        
        # Create vendor profile
        vendor = VendorProfile(
            user_id=current_user_id,
            business_name=data['business_name'],
            business_registration=data['business_registration'],
            category=data['category'],
            description=data['description'],
            years_in_operation=data['years_in_operation'],
            county=data['county'],
            town=data['town'],
            address=data['address'],
            phone=data['phone'],
            email=data['email'],
            website=data.get('website'),
            status='pending'  # Needs admin approval
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        return jsonify({
            'message': 'Vendor registration submitted successfully. Awaiting admin approval.',
            'vendor': vendor.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/marketplace', methods=['GET'])
def get_vendors():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        county = request.args.get('county')
        
        query = VendorProfile.query.filter_by(status='verified', is_featured=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if county:
            query = query.filter_by(county=county)
        
        vendors = query.order_by(VendorProfile.rating.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'vendors': [vendor.to_dict() for vendor in vendors.items],
            'total': vendors.total,
            'pages': vendors.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/<vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    try:
        vendor = VendorProfile.query.get(vendor_id)
        
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
        
        if vendor.status != 'verified':
            return jsonify({'error': 'Vendor not verified'}), 403
        
        # Get vendor services
        services = VendorService.query.filter_by(vendor_id=vendor_id, is_available=True).all()
        
        vendor_data = vendor.to_dict()
        vendor_data['services'] = [service.to_dict() for service in services]
        
        return jsonify(vendor_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/<vendor_id>/services', methods=['POST'])
@jwt_required()
def add_service(vendor_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user owns this vendor profile
        vendor = VendorProfile.query.filter_by(id=vendor_id, user_id=current_user_id).first()
        
        if not vendor:
            return jsonify({'error': 'Vendor not found or unauthorized'}), 404
        
        data = request.get_json()
        
        required_fields = ['name', 'description', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        service = VendorService(
            vendor_id=vendor_id,
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            currency=data.get('currency', 'KES'),
            duration=data.get('duration'),
            is_available=True
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service added successfully',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
