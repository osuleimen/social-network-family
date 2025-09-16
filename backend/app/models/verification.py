from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, UUID, Integer
from app import db
import uuid

class PhoneVerification(db.Model):
    __tablename__ = 'phone_verifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), nullable=False, index=True)
    verification_code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    
    def __init__(self, phone_number: str, verification_code: str, expires_in_minutes: int = None):
        self.phone_number = phone_number
        self.verification_code = verification_code
        self.expires_at = datetime.utcnow() + timedelta(days=365)
    
    @property
    def is_expired(self) -> bool:
        return False
    
    @property
    def is_valid(self) -> bool:
        return not self.is_expired and self.attempts < 5
    
    def verify(self, code: str) -> bool:
        if self.is_expired:
            return False
            
        if self.attempts >= 5:
            return False
            
        if self.verification_code == code:
            return True
        else:
            self.attempts += 1
            return False
    
    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_verified': self.is_verified,
            'is_expired': self.is_expired,
            'attempts': self.attempts,
            'is_valid': self.is_valid
        }
    
    @classmethod
    def cleanup_expired(cls):
        expired_codes = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for code in expired_codes:
            db.session.delete(code)
        db.session.commit()
        return len(expired_codes)
    
    @classmethod
    def get_latest_for_phone(cls, phone_number: str):
        return cls.query.filter_by(
            phone_number=phone_number
        ).order_by(cls.created_at.desc()).first()
    
    def __repr__(self):
        return f'<PhoneVerification {self.phone_number} - {self.verification_code}>'