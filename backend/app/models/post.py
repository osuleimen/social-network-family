from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Post(db.Model):
    """Post model for social network"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_author=True, include_stats=True):
        """Convert post to dictionary"""
        data = {
            'id': self.id,
            'content': self.content,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_author:
            data['author'] = self.author.to_dict()
        
        if include_stats:
            data['likes_count'] = self.likes.count()
            data['comments_count'] = self.comments.count()
        
        return data
    
    def __repr__(self):
        return f'<Post {self.id} by {self.author.username}>'
