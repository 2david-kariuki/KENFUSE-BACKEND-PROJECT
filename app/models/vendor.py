from app import db
from datetime import datetime
import uuid

class VendorProfile(db.Model):
    __tablename__ = 'vendor_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    business_name = db.Column(db.String(200), nullable=False)
    business_registration = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # funeral_home, casket, florist, etc.
    description = db.Column(db.Text, nullable=False)
    years_in_operation = db.Column(db.Integer, nullable=False)
    county = db.Column(db.String(100), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200), nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, verified, suspended, rejected
    is_featured = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    commission_rate = db.Column(db.Float, default=0.10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    services = db.relationship('VendorService', backref='vendor', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_name': self.business_name,
            'category': self.category,
            'description': self.description,
            'county': self.county,
            'town': self.town,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'logo_url': self.logo_url,
            'status': self.status,
            'is_featured': self.is_featured,
            'rating': self.rating,
            'review_count': self.review_count,
            'commission_rate': self.commission_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class VendorService(db.Model):
    __tablename__ = 'vendor_services'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_id = db.Column(db.String(36), db.ForeignKey('vendor_profiles.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='KES')
    duration = db.Column(db.String(50), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'currency': self.currency,
            'duration': self.duration,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
