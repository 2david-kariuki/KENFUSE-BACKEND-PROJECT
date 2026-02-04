# KENFUSE-BACKEND-PROJECT

kenfuse-backend/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── requirements.txt
├── .env
├── .flaskenv
├── run.py
└── setup.sh

REQUIREMENTS.TXT

Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.2
Flask-Bcrypt==1.0.1
Flask-CORS==4.0.0
Flask-Migrate==4.0.5
python-dotenv==1.0.0
psycopg2-binary==2.9.7
PyJWT==2.8.0
requests==2.31.0
reportlab==4.0.4
Pillow==10.0.0
stripe==7.4.0
qrcode==7.4.2
redis==5.0.1


STEP 3: .env file
Create .env:

text
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=kenfuse-secret-key-2024-change-in-production
JWT_SECRET_KEY=jwt-secret-key-2024-change-in-production
DATABASE_URL=postgresql://N/A:N/A@localhost:5432/kenfuse_db
ADMIN_EMAIL=admin@kenfuse.com
ADMIN_PASSWORD=N/A
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
UPLOAD_FOLDER=./uploads


STEP 4: app/config.py
Create app/config.py:

python
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///kenfuse.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@kenfuse.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
    MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')
    MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
    MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL')
    
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    SUBSCRIPTION_PLANS = {
        'free': {'price': 0, 'features': ['basic_will', '1_memorial']},
        'standard': {'price': 500, 'features': ['advanced_will', '5_memorials', 'fundraising']},
        'premium': {'price': 1500, 'features': ['premium_will', 'unlimited_memorials', 'vendor_marketplace', 'priority_support']}
    }
    
    VENDOR_COMMISSION = 0.10  # 10%
    FUNDRAISING_FEE = 0.05    # 5%

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
STEP 5: app/init.py
Create app/__init__.py:

python
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    from app.config import config
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    from app.routes.auth import auth_bp
    from app.routes.wills import wills_bp
    from app.routes.memorials import memorials_bp
    from app.routes.fundraisers import fundraisers_bp
    from app.routes.vendors import vendors_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wills_bp, url_prefix='/api/wills')
    app.register_blueprint(memorials_bp, url_prefix='/api/memorials')
    app.register_blueprint(fundraisers_bp, url_prefix='/api/fundraisers')
    app.register_blueprint(vendors_bp, url_prefix='/api/vendors')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data["sub"]
        return User.query.get(identity)
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
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
            phone='+254700000000',
            first_name='Admin',
            last_name='Kenfuse',
            role='admin',
            is_verified=True,
            is_active=True
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
STEP 6: Models
Create app/models/__init__.py:

python
from .user import User
from .will import Will
from .memorial import Memorial, Tribute
from .fundraiser import Fundraiser, Donation
from .vendor import VendorProfile, VendorService
from .payment import Payment
Create app/models/user.py:

python
from app import db, bcrypt
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='family')
    subscription_plan = db.Column(db.String(20), default='free')
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'subscription_plan': self.subscription_plan,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }
Create app/models/will.py:

python
from app import db
from datetime import datetime
import uuid

class Will(db.Model):
    __tablename__ = 'wills'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft')
    beneficiaries = db.Column(db.JSON, nullable=True)
    pdf_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='wills')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
Create app/models/memorial.py:

python
from app import db
from datetime import datetime
import uuid

class Memorial(db.Model):
    __tablename__ = 'memorials'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    deceased_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    date_of_passing = db.Column(db.Date, nullable=True)
    biography = db.Column(db.Text, nullable=True)
    visibility = db.Column(db.String(20), default='public')
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='memorials')
    
    def to_dict(self):
        return {
            'id': self.id,
            'deceased_name': self.deceased_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'date_of_passing': self.date_of_passing.isoformat() if self.date_of_passing else None,
            'visibility': self.visibility,
            'location': self.location,
            'created_at': self.created_at.isoformat()
        }
Create app/models/fundraiser.py:

python
from app import db
from datetime import datetime
import uuid

class Fundraiser(db.Model):
    __tablename__ = 'fundraisers'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='KES')
    status = db.Column(db.String(20), default='active')
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        progress = (self.current_amount / self.target_amount * 100) if self.target_amount > 0 else 0
        return {
            'id': self.id,
            'title': self.title,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'progress_percentage': min(100, progress),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
Create app/models/payment.py:

python
from app import db
from datetime import datetime
import uuid

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
STEP 7: Routes
Create app/routes/auth.py:

python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bP

