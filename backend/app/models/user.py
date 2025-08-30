from app import db
from datetime import datetime
import bcrypt
from sqlalchemy.orm import relationship

class User(db.Model):
    """User model for social network"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Integration with Gramps family tree
    gramps_person_id = db.Column(db.String(50), unique=True)
    gramps_tree_id = db.Column(db.String(50))
    
    # Relationships
    posts = relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Follow relationships
    following = relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref='followed',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Notifications
    notifications = relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, first_name, last_name, **kwargs):
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password)
        self.first_name = first_name
        self.last_name = last_name
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def _hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'gramps_person_id': self.gramps_person_id,
            'gramps_tree_id': self.gramps_tree_id,
            'followers_count': self.followers.count(),
            'following_count': self.following.count(),
            'posts_count': self.posts.count()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
