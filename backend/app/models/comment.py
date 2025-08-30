from app import db
from datetime import datetime

class Comment(db.Model):
    """Comment model for social network"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for nested comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self, include_author=True):
        """Convert comment to dictionary"""
        data = {
            'id': self.id,
            'content': self.content,
            'post_id': self.post_id,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'replies_count': len(self.replies)
        }
        
        if include_author:
            data['author'] = self.author.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>'
