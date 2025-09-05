from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class Comment(db.Model):
    __tablename__ = 'social_comments'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('social_users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('social_posts.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship('User', backref='comments')
    
    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'author_id': self.author_id,
            'author': self.author.to_dict() if self.author else None,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>'
