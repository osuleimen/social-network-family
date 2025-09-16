from sqlalchemy import Column, Text, DateTime, ForeignKey, UUID, Boolean
from sqlalchemy.sql import func
from app import db
import uuid

class Comment(db.Model):
    __tablename__ = 'social_comments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey('social_posts.id'), nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('social_comments.id'), nullable=True)
    edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self, requesting_user=None):
        """Convert comment to dictionary"""
        return {
            'id': str(self.id),
            'text': self.text,
            'author_id': str(self.author_id),
            'post_id': str(self.post_id),
            'parent_comment_id': str(self.parent_comment_id) if self.parent_comment_id else None,
            'edited': self.edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def can_edit(self, user_id):
        """Check if user can edit this comment"""
        return self.author_id == user_id
    
    def can_delete(self, user_id, user_role=None):
        """Check if user can delete this comment"""
        if self.author_id == user_id:
            return True
        if user_role and user_role in ['moderator', 'admin', 'superadmin']:
            return True
        return False
    
    @classmethod
    def get_post_comments(cls, post_id, parent_id=None, limit=20, offset=0):
        """Get comments for a post with threading support"""
        query = cls.query.filter_by(post_id=post_id)
        
        if parent_id is None:
            query = query.filter_by(parent_comment_id=None)
        else:
            query = query.filter_by(parent_comment_id=parent_id)
        
        return query.order_by(cls.created_at.asc()).offset(offset).limit(limit).all()
    
    def __repr__(self):
        return f'<Comment {self.id}>'