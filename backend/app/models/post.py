from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app import db

class Post(db.Model):
    __tablename__ = 'social_posts'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('social_users.id'), nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship('User', backref='posts')
    comments = relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = relationship('Like', lazy='dynamic', cascade='all, delete-orphan')
    media = relationship('Media', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert post to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'author_id': self.author_id,
            'author': self.author.to_dict() if self.author else None,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'likes_count': self.likes.count() if hasattr(self, 'likes') else 0,
            'comments_count': self.comments.count() if hasattr(self, 'comments') else 0,
            'media': [media.to_dict() for media in self.media.all()] if hasattr(self, 'media') else []
        }
    
    def __repr__(self):
        return f'<Post {self.id}>'
