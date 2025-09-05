from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app import db

class Like(db.Model):
    __tablename__ = 'social_likes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('social_users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('social_posts.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship('User', backref='likes')
    post = relationship('Post')
    
    # Ensure a user can only like a post once
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    
    def to_dict(self):
        """Convert like to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Like {self.user_id} -> {self.post_id}>'
