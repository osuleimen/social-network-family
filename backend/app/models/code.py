from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.sql import func
from app import db
import hashlib
import uuid

class Code(db.Model):
    __tablename__ = 'social_codes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=True)
    identifier = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    code_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    def is_expired(self):
        return False
    
    def verify(self, input_code: str):
        if not self.is_active:
            return False
        
        input_hash = hashlib.sha256(input_code.encode('utf-8')).hexdigest()
        if input_hash != self.code_hash:
            return False
        
        self.verified_at = func.now()
        return True
    
    def deactivate(self):
        self.is_active = False
    
    @classmethod
    def create_code(cls, identifier: str, code_type: str, user_id=None):
        import secrets
        
        code = f"{secrets.randbelow(1000000):06d}"
        code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
        
        new_code = cls(
            user_id=user_id,
            identifier=identifier,
            type=code_type,
            code_hash=code_hash,
            expires_at=None
        )
        
        return new_code, code
    
    @classmethod
    def find_active_code(cls, identifier: str, code: str):
        all_codes = cls.query.filter_by(identifier=identifier).all()
        
        for code_obj in all_codes:
            import hashlib
            input_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
            if input_hash == code_obj.code_hash:
                return code_obj
        
        return None
    
    @classmethod
    def find_active_code_for_identifier(cls, identifier: str):
        return cls.query.filter_by(
            identifier=identifier,
            is_active=True
        ).first()
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'identifier': self.identifier,
            'type': self.type,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }
    
    def __repr__(self):
        return f'<Code {self.identifier}: [HASHED]>'