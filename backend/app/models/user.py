from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date
from sqlalchemy.sql import func
from app import db

class User(db.Model):
    __tablename__ = 'social_users'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False)  # Primary identifier
    username = Column(String(80), unique=True, nullable=True)  # Optional, can be set later
    email = Column(String(120), unique=True, nullable=True)    # Optional
    first_name = Column(String(100), nullable=True)            # Can be set after registration
    last_name = Column(String(100), nullable=True)             # Can be set after registration
    bio = Column(Text)
    birth_date = Column(Date)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)  # Verified by SMS
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Gramps integration fields
    gramps_person_id = Column(String(50), unique=True)
    gramps_tree_id = Column(String(50))
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'gramps_person_id': self.gramps_person_id,
            'gramps_tree_id': self.gramps_tree_id
        }
    
    @classmethod
    def find_by_phone(cls, phone_number: str):
        """Find user by phone number"""
        return cls.query.filter_by(phone_number=phone_number).first()
    
    @classmethod
    def create_from_phone(cls, phone_number: str, **kwargs):
        """Create new user with phone number"""
        user = cls(
            phone_number=phone_number,
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            **{k: v for k, v in kwargs.items() if k not in ['first_name', 'last_name']}
        )
        return user
    
    def __repr__(self):
        return f'<User {self.phone_number}>'
