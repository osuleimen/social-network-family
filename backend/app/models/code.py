from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app import db
import hashlib

class Code(db.Model):
    __tablename__ = 'social_codes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('social_users.id'), nullable=True)  # Can be null for unregistered users
    identifier = Column(String(255), nullable=False)  # phone/email for which code was generated
    type = Column(String(20), nullable=False)  # 'phone' or 'email'
    code_hash = Column(String(255), nullable=False)  # bcrypt hash of 6-digit code
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Nullable - codes don't expire per TZ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    user = relationship('User', backref='codes')
    
    def is_expired(self):
        """Check if code is expired - per TZ codes don't expire"""
        return False  # Codes don't expire per technical requirements
    
    def verify(self, input_code: str):
        """Verify the code using hash comparison"""
        if not self.is_active:
            return False
        
        # Verify using hash comparison
        input_hash = hashlib.sha256(input_code.encode('utf-8')).hexdigest()
        if input_hash != self.code_hash:
            return False
        
        # Mark as verified but НЕ деактивируем - код может использоваться повторно
        self.verified_at = func.now()
        # self.is_active = False  # Убираем деактивацию
        return True
    
    def deactivate(self):
        """Deactivate the code"""
        self.is_active = False
    
    @classmethod
    def create_code(cls, identifier: str, code_type: str, user_id=None):
        """Create a new verification code"""
        import secrets
        
        # НЕ деактивируем старые коды - они могут использоваться повторно
        
        # Generate 6-digit code
        code = f"{secrets.randbelow(1000000):06d}"
        
        # Hash the code with SHA256
        code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
        
        # Create new code (no expiration per TZ)
        new_code = cls(
            user_id=user_id,
            identifier=identifier,
            type=code_type,
            code_hash=code_hash,
            expires_at=None  # No expiration per technical requirements
        )
        
        return new_code, code  # Return both the model and the plain code for sending
    
    @classmethod
    def find_active_code(cls, identifier: str, code: str):
        """Find code for identifier and verify it (including previously used codes)"""
        # Ищем ВСЕ коды для идентификатора, не только активные
        all_codes = cls.query.filter_by(identifier=identifier).all()
        
        # Check each code
        for code_obj in all_codes:
            # Verify hash without modifying the object yet
            import hashlib
            input_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
            if input_hash == code_obj.code_hash:
                return code_obj
        
        return None
    
    @classmethod
    def find_active_code_for_identifier(cls, identifier: str):
        """Find any active code for identifier"""
        return cls.query.filter_by(
            identifier=identifier,
            is_active=True
        ).first()
    
    def to_dict(self):
        """Convert code to dictionary"""
        return {
            'id': self.id,
            'identifier': self.identifier,
            'type': self.type,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }
    
    def __repr__(self):
        return f'<Code {self.identifier}: [HASHED]>'
