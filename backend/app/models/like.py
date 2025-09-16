from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, UUID
from sqlalchemy.sql import func
from app import db
import uuid

class Like(db.Model):
    __tablename__ = 'social_likes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey('social_posts.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Ensure a user can only like a post once (idempotency)
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    
    def to_dict(self):
        """Convert like to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'post_id': str(self.post_id),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def toggle_like(cls, user_id, post_id):
        """Toggle like for a post (idempotent)"""
        existing_like = cls.query.filter_by(user_id=user_id, post_id=post_id).first()
        
        if existing_like:
            # Unlike - remove the like
            db.session.delete(existing_like)
            # Decrement post likes count
            from app.models.post import Post
            post = Post.query.get(post_id)
            if post:
                post.decrement_likes_count()
            return False, "unliked"
        else:
            # Like - create new like
            new_like = cls(user_id=user_id, post_id=post_id)
            db.session.add(new_like)
            # Increment post likes count
            from app.models.post import Post
            post = Post.query.get(post_id)
            if post:
                post.increment_likes_count()
            return True, "liked"
    
    def __repr__(self):
        return f'<Like {self.user_id} -> {self.post_id}>'