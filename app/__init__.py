from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.wills import wills_bp
    from app.routes.memorials import memorials_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wills_bp, url_prefix='/api/wills')
    app.register_blueprint(memorials_bp, url_prefix='/api/memorials')
    
    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # JWT configuration - FIXED
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        # user should be the user ID string, not the User object
        return user
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data["sub"]  # This should be the user ID
        return User.query.get(identity)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
        create_admin_user(app)
    
    return app

def create_admin_user(app):
    from app.models import User
    from datetime import datetime
    
    admin = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
    if not admin:
        admin = User(
            email=app.config['ADMIN_EMAIL'],
            phone=app.config['ADMIN_PHONE'],
            first_name='Admin',
            last_name='Kenfuse',
            role='admin',
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin user created: {admin.email}")
