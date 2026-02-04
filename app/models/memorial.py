from app import db
from datetime import datetime
import uuid

class Memorial(db.Model):
    __tablename__ = 'memorials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    deceased_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    date_of_passing = db.Column(db.Date, nullable=False)
    biography = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    visibility = db.Column(db.String(20), default='public')  # public, private, family
    location = db.Column(db.String(200), nullable=True)
    obituary = db.Column(db.Text, nullable=True)
    funeral_details = db.Column(db.JSON, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tributes = db.relationship('Tribute', backref='memorial', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'deceased_name': self.deceased_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'date_of_passing': self.date_of_passing.isoformat() if self.date_of_passing else None,
            'biography': self.biography,
            'photo_url': self.photo_url,
            'visibility': self.visibility,
            'location': self.location,
            'obituary': self.obituary,
            'funeral_details': self.funeral_details,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Tribute(db.Model):
    __tablename__ = 'tributes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memorial_id = db.Column(db.String(36), db.ForeignKey('memorials.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=True)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'author_name': self.author_name,
            'relationship': self.relationship,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
