from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date
from sqlalchemy.sql import func
from app import db

class User(db.Model):
    __tablename__ = 'social_users'
    
    id = Column(Integer, primary_key=True)
    identifier = Column(String(255), unique=True, nullable=False)  # Primary identifier (phone/email/google_id)
    type = Column(String(20), nullable=False)  # 'phone', 'email', 'google'
    
    # Legacy fields for compatibility
    phone_number = Column(String(20), unique=True, nullable=True)  # Optional for email/Google users
    username = Column(String(80), unique=True, nullable=True)  # Optional, can be set later
    email = Column(String(120), unique=True, nullable=True)    # Primary identifier for email users
    first_name = Column(String(100), nullable=True)            # Can be set after registration
    last_name = Column(String(100), nullable=True)             # Can be set after registration
    bio = Column(Text)
    birth_date = Column(Date)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)  # Verified by SMS/Email/Google
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Authentication method tracking
    auth_method = Column(String(20), default='phone')  # 'phone', 'email', 'google'
    
    # Google OAuth fields
    google_id = Column(String(100), unique=True, nullable=True)
    google_picture = Column(String(255), nullable=True)
    
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
            'avatar_url': self.avatar_url or self.google_picture,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'auth_method': self.auth_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'gramps_person_id': self.gramps_person_id,
            'gramps_tree_id': self.gramps_tree_id
        }
    
    @classmethod
    def find_by_identifier(cls, identifier: str):
        """Find user by identifier (phone/email/google_id)"""
        return cls.query.filter_by(identifier=identifier).first()
    
    @classmethod
    def find_by_phone(cls, phone_number: str):
        """Find user by phone number"""
        return cls.query.filter_by(phone_number=phone_number).first()
    
    @classmethod
    def find_by_email(cls, email: str):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_google_id(cls, google_id: str):
        """Find user by Google ID"""
        return cls.query.filter_by(google_id=google_id).first()
    
    @classmethod
    def create_from_identifier(cls, identifier: str, user_type: str, **kwargs):
        """Create new user with identifier and type"""
        user = cls(
            identifier=identifier,
            type=user_type,
            phone_number=identifier if user_type == 'phone' else None,
            email=identifier if user_type == 'email' else None,
            google_id=identifier if user_type == 'google' else None,
            auth_method=user_type,
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            **{k: v for k, v in kwargs.items() if k not in ['first_name', 'last_name']}
        )
        return user
    
    @classmethod
    def create_from_phone(cls, phone_number: str, **kwargs):
        """Create new user with phone number"""
        return cls.create_from_identifier(phone_number, 'phone', **kwargs)
    
    @classmethod
    def create_from_email(cls, email: str, **kwargs):
        """Create new user with email"""
        return cls.create_from_identifier(email, 'email', **kwargs)
    
    @classmethod
    def create_from_google(cls, google_data: dict, **kwargs):
        """Create new user from Google OAuth data"""
        user = cls(
            identifier=google_data.get('google_id'),
            type='google',
            email=google_data.get('email'),
            google_id=google_data.get('google_id'),
            google_picture=google_data.get('picture'),
            auth_method='google',
            first_name=google_data.get('first_name', ''),
            last_name=google_data.get('last_name', ''),
            is_verified=google_data.get('verified_email', True),
            **{k: v for k, v in kwargs.items() if k not in ['first_name', 'last_name']}
        )
        return user
    
    def __repr__(self):
        return f'<User {self.phone_number}>'
