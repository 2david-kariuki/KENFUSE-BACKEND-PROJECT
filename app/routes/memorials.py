from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Memorial, Tribute, User
from datetime import datetime

memorials_bp = Blueprint('memorials', __name__)

@memorials_bp.route('/', methods=['POST'])
@jwt_required()
def create_memorial():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['deceased_name', 'date_of_birth', 'date_of_passing']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Check subscription limits
        if user.subscription_plan == 'free':
            memorial_count = Memorial.query.filter_by(user_id=current_user_id).count()
            if memorial_count >= 1:
                return jsonify({'error': 'Free plan limited to 1 memorial. Upgrade for more.'}), 403
        
        # Parse dates
        try:
            dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            dop = datetime.strptime(data['date_of_passing'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create memorial
        memorial = Memorial(
            user_id=current_user_id,
            deceased_name=data['deceased_name'],
            date_of_birth=dob,
            date_of_passing=dop,
            biography=data.get('biography'),
            visibility=data.get('visibility', 'public'),
            location=data.get('location'),
            obituary=data.get('obituary'),
            funeral_details=data.get('funeral_details')
        )
        
        db.session.add(memorial)
        db.session.commit()
        
        return jsonify({
            'message': 'Memorial created successfully',
            'memorial': memorial.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memorials_bp.route('/', methods=['GET'])
def get_memorials():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        visibility = request.args.get('visibility', 'public')
        
        # Base query
        query = Memorial.query
        
        # Filter by visibility
        if visibility == 'public':
            query = query.filter_by(visibility='public')
        
        # Pagination
        memorials = query.order_by(Memorial.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'memorials': [memorial.to_dict() for memorial in memorials.items],
            'total': memorials.total,
            'pages': memorials.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memorials_bp.route('/<memorial_id>', methods=['GET'])
def get_memorial(memorial_id):
    try:
        memorial = Memorial.query.get(memorial_id)
        
        if not memorial:
            return jsonify({'error': 'Memorial not found'}), 404
        
        # Check visibility
        if memorial.visibility != 'public':
            current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
            if not current_user_id or memorial.user_id != current_user_id:
                return jsonify({'error': 'This memorial is private'}), 403
        
        # Get tributes
        tributes = Tribute.query.filter_by(memorial_id=memorial_id).all()
        
        memorial_data = memorial.to_dict()
        memorial_data['tributes'] = [tribute.to_dict() for tribute in tributes]
        
        return jsonify(memorial_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memorials_bp.route('/<memorial_id>/tributes', methods=['POST'])
def add_tribute(memorial_id):
    try:
        memorial = Memorial.query.get(memorial_id)
        
        if not memorial:
            return jsonify({'error': 'Memorial not found'}), 404
        
        data = request.get_json()
        
        if 'message' not in data or 'author_name' not in data:
            return jsonify({'error': 'Message and author name required'}), 400
        
        current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        
        tribute = Tribute(
            memorial_id=memorial_id,
            user_id=current_user_id,
            message=data['message'],
            author_name=data['author_name'],
            relationship=data.get('relationship'),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        db.session.add(tribute)
        db.session.commit()
        
        return jsonify({
            'message': 'Tribute added successfully',
            'tribute': tribute.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memorials_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_memorials():
    try:
        current_user_id = get_jwt_identity()
        
        memorials = Memorial.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'memorials': [memorial.to_dict() for memorial in memorials],
            'count': len(memorials)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
