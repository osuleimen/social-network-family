from sqlalchemy import Column, String, Boolean, DateTime, UUID, Integer
from sqlalchemy.sql import func
from app import db
import uuid
from datetime import datetime, timedelta

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(120), nullable=False, index=True)
    verification_code = Column(String(10), nullable=False)
    attempts = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    @property
    def is_expired(self):
        return False
    
    def verify(self, code: str) -> bool:
        if not self.is_valid or self.is_expired:
            return False
            
        if self.attempts >= 5:
            self.is_valid = False
            return False
            
        self.attempts += 1
        
        if self.verification_code == code:
            return True
            
        return False
    
    @classmethod
    def create_verification(cls, email: str, code: str, expires_minutes: int = None):
        expires_at = datetime.utcnow() + timedelta(days=365)
        
        verification = cls(
            email=email,
            verification_code=code,
            expires_at=expires_at
        )
        
        return verification
    
    @classmethod
    def get_latest_for_email(cls, email: str):
        from datetime import timezone
        now = datetime.now(timezone.utc)
        return cls.query.filter_by(
            email=email,
            is_valid=True
        ).filter(
            cls.expires_at > now
        ).order_by(cls.created_at.desc()).first()
    
    @classmethod
    def invalidate_old_verifications(cls, email: str):
        cls.query.filter_by(email=email).update({'is_valid': False})
    
    def __repr__(self):
        return f'<EmailVerification {self.email}>'