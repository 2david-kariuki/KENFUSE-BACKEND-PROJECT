from app import db
from datetime import datetime
import uuid
import json

class Will(db.Model):
    __tablename__ = 'wills'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft')
    beneficiaries = db.Column(db.JSON, nullable=True)
    pdf_url = db.Column(db.String(500), nullable=True)
    pdf_generated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'beneficiaries': self.beneficiaries,
            'pdf_url': self.pdf_url,
            'pdf_generated_at': self.pdf_generated_at.isoformat() if self.pdf_generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
