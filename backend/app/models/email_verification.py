from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app import db
import secrets
import string
from datetime import datetime, timedelta

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False, index=True)
    verification_code = Column(String(10), nullable=False)
    attempts = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    @property
    def is_expired(self):
        """Check if verification code is expired - коды больше не истекают"""
        return False  # Коды больше не истекают
    
    def verify(self, code: str) -> bool:
        """
        Verify the provided code
        
        Args:
            code: Code to verify
            
        Returns:
            True if code is correct, False otherwise
        """
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
        """
        Create new email verification record
        
        Args:
            email: Email address
            code: Verification code
            expires_minutes: Minutes until expiration (не используется - коды не истекают)
            
        Returns:
            EmailVerification instance
        """
        # Код не истекает - устанавливаем дату на год вперед
        expires_at = datetime.utcnow() + timedelta(days=365)
        
        verification = cls(
            email=email,
            verification_code=code,
            expires_at=expires_at
        )
        
        return verification
    
    @classmethod
    def get_latest_for_email(cls, email: str):
        """
        Get latest valid verification for email
        
        Args:
            email: Email address
            
        Returns:
            Latest EmailVerification or None
        """
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
        """
        Invalidate old verifications for email
        
        Args:
            email: Email address
        """
        cls.query.filter_by(email=email).update({'is_valid': False})
    
    def __repr__(self):
        return f'<EmailVerification {self.email}>'
