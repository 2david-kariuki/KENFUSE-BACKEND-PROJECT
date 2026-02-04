from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, VendorProfile, Fundraiser, Memorial, Payment

admin_bp = Blueprint('admin', __name__)

def is_admin():
    """Check if current user is admin"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user and user.role == 'admin'

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get statistics
        total_users = User.query.count()
        total_vendors = VendorProfile.query.count()
        total_fundraisers = Fundraiser.query.count()
        total_memorials = Memorial.query.count()
        
        # Get recent payments
        recent_payments = Payment.query\
            .order_by(Payment.created_at.desc())\
            .limit(10)\
            .all()
        
        # Get pending vendor approvals
        pending_vendors = VendorProfile.query\
            .filter_by(status='pending')\
            .limit(10)\
            .all()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_vendors': total_vendors,
                'total_fundraisers': total_fundraisers,
                'total_memorials': total_memorials
            },
            'recent_payments': [payment.to_dict() for payment in recent_payments],
            'pending_vendors': [vendor.to_dict() for vendor in pending_vendors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/vendors/pending', methods=['GET'])
@jwt_required()
def get_pending_vendors():
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        pending_vendors = VendorProfile.query.filter_by(status='pending').all()
        
        return jsonify({
            'vendors': [vendor.to_dict() for vendor in pending_vendors],
            'count': len(pending_vendors)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/vendors/<vendor_id>/approve', methods=['PUT'])
@jwt_required()
def approve_vendor(vendor_id):
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        vendor = VendorProfile.query.get(vendor_id)
        
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
        
        vendor.status = 'verified'
        db.session.commit()
        
        return jsonify({
            'message': 'Vendor approved successfully',
            'vendor': vendor.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/vendors/<vendor_id>/reject', methods=['PUT'])
@jwt_required()
def reject_vendor(vendor_id):
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        vendor = VendorProfile.query.get(vendor_id)
        
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
        
        vendor.status = 'rejected'
        if data and 'reason' in data:
            vendor.rejection_reason = data['reason']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vendor rejected',
            'vendor': vendor.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/fundraisers/pending', methods=['GET'])
@jwt_required()
def get_pending_fundraisers():
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        pending_fundraisers = Fundraiser.query.filter_by(is_verified=False).all()
        
        return jsonify({
            'fundraisers': [fundraiser.to_dict() for fundraiser in pending_fundraisers],
            'count': len(pending_fundraisers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/fundraisers/<fundraiser_id>/verify', methods=['PUT'])
@jwt_required()
def verify_fundraiser(fundraiser_id):
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        fundraiser = Fundraiser.query.get(fundraiser_id)
        
        if not fundraiser:
            return jsonify({'error': 'Fundraiser not found'}), 404
        
        fundraiser.is_verified = True
        db.session.commit()
        
        return jsonify({
            'message': 'Fundraiser verified successfully',
            'fundraiser': fundraiser.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<user_id>/toggle-status', methods=['PUT'])
@jwt_required()
def toggle_user_status(user_id):
    try:
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        
        return jsonify({
            'message': f'User {status} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
