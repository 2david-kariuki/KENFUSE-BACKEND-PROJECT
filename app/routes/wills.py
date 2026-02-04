from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Will, User
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

wills_bp = Blueprint('wills', __name__)

@wills_bp.route('/', methods=['POST'])
@jwt_required()
def create_will():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content', 'beneficiaries']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Check subscription limits
        if user.subscription_plan == 'free':
            will_count = Will.query.filter_by(user_id=current_user_id).count()
            if will_count >= 1:
                return jsonify({'error': 'Free plan limited to 1 will. Upgrade for more.'}), 403
        
        # Create will
        will = Will(
            user_id=current_user_id,
            title=data['title'],
            content=data['content'],
            beneficiaries=data['beneficiaries'],
            witnesses=data.get('witnesses'),
            assets=data.get('assets'),
            status=data.get('status', 'draft')
        )
        
        db.session.add(will)
        db.session.commit()
        
        return jsonify({
            'message': 'Will created successfully',
            'will': will.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wills_bp.route('/', methods=['GET'])
@jwt_required()
def get_wills():
    try:
        current_user_id = get_jwt_identity()
        
        wills = Will.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'wills': [will.to_dict() for will in wills],
            'count': len(wills)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wills_bp.route('/<will_id>', methods=['GET'])
@jwt_required()
def get_will(will_id):
    try:
        current_user_id = get_jwt_identity()
        
        will = Will.query.filter_by(id=will_id, user_id=current_user_id).first()
        
        if not will:
            return jsonify({'error': 'Will not found'}), 404
        
        return jsonify({
            'will': will.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wills_bp.route('/<will_id>/export-pdf', methods=['GET'])
@jwt_required()
def export_will_pdf(will_id):
    try:
        current_user_id = get_jwt_identity()
        
        will = Will.query.filter_by(id=will_id, user_id=current_user_id).first()
        
        if not will:
            return jsonify({'error': 'Will not found'}), 404
        
        # Create PDF buffer
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add content to PDF
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Last Will and Testament")
        p.drawString(100, 730, f"Title: {will.title}")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 700, f"Created by: {will.user.first_name} {will.user.last_name}")
        
        # Add will content
        y_position = 650
        p.setFont("Helvetica", 11)
        for line in will.content.split('\n'):
            if y_position < 50:  # New page if needed
                p.showPage()
                y_position = 750
                p.setFont("Helvetica", 11)
            
            if line.strip():
                p.drawString(100, y_position, line[:80])
                y_position -= 20
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        
        # Update will with PDF URL
        will.pdf_url = f'/api/wills/{will.id}/pdf'
        db.session.commit()
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"will_{will.title.replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wills_bp.route('/<will_id>', methods=['PUT'])
@jwt_required()
def update_will(will_id):
    try:
        current_user_id = get_jwt_identity()
        
        will = Will.query.filter_by(id=will_id, user_id=current_user_id).first()
        
        if not will:
            return jsonify({'error': 'Will not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            will.title = data['title']
        if 'content' in data:
            will.content = data['content']
        if 'beneficiaries' in data:
            will.beneficiaries = data['beneficiaries']
        if 'witnesses' in data:
            will.witnesses = data['witnesses']
        if 'assets' in data:
            will.assets = data['assets']
        if 'status' in data:
            will.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Will updated successfully',
            'will': will.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
