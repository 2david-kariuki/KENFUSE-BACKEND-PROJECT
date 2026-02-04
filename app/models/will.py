from app import db
from datetime import datetime
import uuid

class Will(db.Model):
    __tablename__ = 'wills'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, completed, signed, archived
    witnesses = db.Column(db.JSON, nullable=True)
    beneficiaries = db.Column(db.JSON, nullable=False)
    assets = db.Column(db.JSON, nullable=True)
    pdf_url = db.Column(db.String(500), nullable=True)
    is_digital_signature = db.Column(db.Boolean, default=False)
    signed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'witnesses': self.witnesses,
            'beneficiaries': self.beneficiaries,
            'assets': self.assets,
            'pdf_url': self.pdf_url,
            'is_digital_signature': self.is_digital_signature,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
