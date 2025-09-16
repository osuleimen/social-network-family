from sqlalchemy import Column, String, Text, Date, Boolean, DateTime, ForeignKey, UUID, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app import db
import uuid
import enum
import re
from datetime import datetime

class UserRole(enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class UserStatus(enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DEACTIVATED = "deactivated"

class User(db.Model):
    __tablename__ = 'social_users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String(255), nullable=False, unique=True)  # email or phone
    type = Column(String(20), nullable=False)  # 'email' or 'phone'
    email = Column(String(120), nullable=True, unique=True)
    username = Column(String(30), nullable=True, unique=True)
    profile_slug = Column(String(30), nullable=True, unique=True)
    previous_slugs = Column(JSON, nullable=True)  # Store old slugs for redirects
    display_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True, unique=True)
    date_of_birth = Column(Date, nullable=True)
    bio = Column(Text, nullable=True)
    avatar_media_id = Column(UUID(as_uuid=True), nullable=True)
    website = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    pronouns = Column(String(50), nullable=True)
    private_account = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    auth_method = Column(String(20), nullable=True)  # 'password', 'google', 'phone'
    google_id = Column(String(100), nullable=True, unique=True)
    google_picture = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    banned_until = Column(DateTime(timezone=True), nullable=True)
    gramps_person_id = Column(String(100), nullable=True)
    gramps_tree_id = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self, include_pii=False, requesting_user=None):
        """Convert user to dictionary with PII protection"""
        data = {
            'id': str(self.id),
            'username': self.username,
            'profile_slug': self.profile_slug,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_media_id': str(self.avatar_media_id) if self.avatar_media_id else None,
            'website': self.website,
            'location': self.location,
            'pronouns': self.pronouns,
            'private_account': self.private_account,
            'verified': self.verified,
            'role': self.role.value if self.role else 'user',
            'status': self.status.value if self.status else 'active',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include PII only if requested and user has permission
        if include_pii or self.can_view_pii(requesting_user):
            data.update({
                'email': self.email,
                'phone_number': self.phone_number,
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'gramps_person_id': self.gramps_person_id,
                'gramps_tree_id': self.gramps_tree_id
            })
        
        return data

    def set_password(self, password):
        """Set password hash"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def is_superadmin(self):
        """Check if user is SuperAdmin"""
        return self.role == UserRole.SUPERADMIN

    def is_admin(self):
        """Check if user is Admin"""
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]

    def can_admin(self):
        """Check if user can perform admin actions"""
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]

    def can_moderate(self):
        """Check if user can moderate content"""
        return self.role in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPERADMIN]

    def can_view_pii(self, requesting_user):
        """Check if requesting user can view PII"""
        if not requesting_user:
            return False
        if requesting_user.id == self.id:
            return True
        if requesting_user.can_admin():
            return True
        return False

    def can_impersonate(self):
        """Check if user can impersonate others"""
        return self.is_superadmin()

    def generate_profile_slug(self, base_string):
        """Generate URL-safe profile slug"""
        if not base_string:
            return None
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\-]', '', base_string.lower())
        slug = re.sub(r'\-+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure it's not empty and not too long
        if not slug or len(slug) > 30:
            slug = f"user-{str(self.id)[:8]}"
        
        # Check for uniqueness
        original_slug = slug
        counter = 1
        while User.query.filter_by(profile_slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        return slug

    def update_username_and_slug(self, new_username):
        """Update username and profile slug"""
        if not new_username:
            return False
        
        # Store old slug for redirects
        if self.profile_slug:
            if not self.previous_slugs:
                self.previous_slugs = []
            if self.profile_slug not in self.previous_slugs:
                self.previous_slugs.append(self.profile_slug)
        
        self.username = new_username
        self.profile_slug = self.generate_profile_slug(new_username)
        return True

    def get_public_profile_url(self):
        """Get public profile URL"""
        if self.profile_slug:
            return f"/profile/{self.profile_slug}"
        return f"/profile/{self.id}"

    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_profile_slug(cls, profile_slug):
        """Find user by profile slug"""
        return cls.query.filter_by(profile_slug=profile_slug).first()

    @classmethod
    def find_by_slug_or_previous(cls, slug):
        """Find user by current or previous slug"""
        user = cls.find_by_profile_slug(slug)
        if user:
            return user
        
        # Search in previous slugs
        return cls.query.filter(cls.previous_slugs.contains([slug])).first()

    @classmethod
    def get_superadmin_count(cls):
        """Get count of SuperAdmin users"""
        return cls.query.filter_by(role=UserRole.SUPERADMIN).count()

    @classmethod
    def find_by_google_id(cls, google_id):
        """Find user by Google ID"""
        return cls.query.filter_by(google_id=google_id).first()

    @classmethod
    def find_by_identifier(cls, identifier):
        """Find user by identifier (email or phone)"""
        return cls.query.filter_by(identifier=identifier).first()

    @classmethod
    def create_from_google(cls, google_data):
        """Create user from Google OAuth data"""
        # Extract data from Google response
        google_id = google_data.get('id')
        email = google_data.get('email')
        name = google_data.get('name', '')
        given_name = google_data.get('given_name', '')
        family_name = google_data.get('family_name', '')
        picture = google_data.get('picture')
        
        # Create display name
        display_name = name or f"{given_name} {family_name}".strip()
        
        # Create username from email
        username = email.split('@')[0] if email else f"user_{google_id[:8]}"
        
        # Ensure username is unique
        original_username = username
        counter = 1
        while cls.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = cls(
            identifier=email,
            type='email',
            email=email,
            username=username,
            display_name=display_name,
            google_id=google_id,
            google_picture=picture,
            auth_method='google',
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            verified=True
        )
        
        return user

    @classmethod
    def create_from_identifier(cls, identifier, user_type, **kwargs):
        """Create user from identifier (email or phone)"""
        if user_type == 'email':
            email = identifier
            username = email.split('@')[0] if email else f"user_{uuid.uuid4().hex[:8]}"
            display_name = username
        else:  # phone
            phone_number = identifier
            username = f"user_{phone_number[-4:]}"  # Use last 4 digits
            display_name = f"User {phone_number[-4:]}"
            email = None
        
        # Ensure username is unique
        original_username = username
        counter = 1
        while cls.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = cls(
            identifier=identifier,
            type=user_type,
            email=email,
            phone_number=phone_number if user_type == 'phone' else None,
            username=username,
            display_name=display_name,
            auth_method='phone' if user_type == 'phone' else 'email',
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            verified=True if user_type == 'phone' else False,
            **kwargs
        )
        
        return user

    @classmethod
    def create_superadmin(cls, identifier, user_type, email=None, display_name=None, username=None, **kwargs):
        """Create SuperAdmin user"""
        superadmin = cls(
            identifier=identifier,
            type=user_type,
            email=email,
            display_name=display_name,
            username=username,
            role=UserRole.SUPERADMIN,
            status=UserStatus.ACTIVE,
            verified=True,
            **kwargs
        )
        return superadmin

    def __repr__(self):
        return f'<User {self.username or self.email or self.phone_number}>'