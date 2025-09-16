from sqlalchemy import Column, Text, DateTime, ForeignKey, UUID, Enum, JSON, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app import db
import uuid
import enum
import re

class PostPrivacy(enum.Enum):
    PUBLIC = "public"
    FOLLOWERS_ONLY = "followers_only"
    PRIVATE = "private"

class Post(db.Model):
    __tablename__ = 'social_posts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    caption = Column(Text, nullable=False)  # Post content
    media = Column(JSON, default=list)  # List of media_id + metadata
    hashtags = Column(JSON, nullable=True)  # Extracted hashtags
    mentions = Column(JSON, nullable=True)  # Extracted mentions
    privacy = Column(Enum(PostPrivacy), default=PostPrivacy.PUBLIC, nullable=False)
    likes_count = Column(Integer, default=0)  # Denormalized counter
    comments_count = Column(Integer, default=0)  # Denormalized counter
    is_edited = Column(Boolean, default=False)
    edit_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self, requesting_user=None):
        """Convert post to dictionary"""
        return {
            'id': str(self.id),
            'author_id': str(self.author_id),
            'author': self.author.to_dict(requesting_user=requesting_user) if self.author else None,
            'caption': self.caption,
            'media': self.media or [],
            'hashtags': self.hashtags or [],
            'mentions': self.mentions or [],
            'privacy': self.privacy.value if self.privacy else 'public',
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'is_edited': self.is_edited,
            'edit_count': self.edit_count,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def extract_hashtags(self):
        """Extract hashtags from caption"""
        if not self.caption:
            return []
        hashtags = re.findall(r'#(\w+)', self.caption)
        return list(set(hashtags))  # Remove duplicates

    def extract_mentions(self):
        """Extract mentions from caption"""
        if not self.caption:
            return []
        mentions = re.findall(r'@(\w+)', self.caption)
        return list(set(mentions))  # Remove duplicates

    def increment_likes_count(self):
        """Atomically increment likes count"""
        self.likes_count = (self.likes_count or 0) + 1

    def decrement_likes_count(self):
        """Atomically decrement likes count"""
        self.likes_count = max((self.likes_count or 0) - 1, 0)

    def increment_comments_count(self):
        """Atomically increment comments count"""
        self.comments_count = (self.comments_count or 0) + 1

    def decrement_comments_count(self):
        """Atomically decrement comments count"""
        self.comments_count = max((self.comments_count or 0) - 1, 0)

    def can_view(self, user_id):
        """Check if user can view this post"""
        if self.is_deleted:
            return False
        
        if self.privacy == PostPrivacy.PUBLIC:
            return True
        
        if self.privacy == PostPrivacy.PRIVATE:
            return user_id == self.author_id
        
        if self.privacy == PostPrivacy.FOLLOWERS_ONLY:
            if user_id == self.author_id:
                return True
            # Check if user follows the author
            from app.models.follow import Follow, FollowStatus
            follow = Follow.query.filter_by(
                follower_id=user_id,
                followed_id=self.author_id,
                status=FollowStatus.ACCEPTED
            ).first()
            return follow is not None
        
        return False

    @classmethod
    def get_popular_posts(cls, limit=20, window_days=None):
        """Get popular posts ordered by likes and recency"""
        query = cls.query.filter_by(is_deleted=False, privacy=PostPrivacy.PUBLIC)
        
        if window_days:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=window_days)
            query = query.filter(cls.created_at >= cutoff_date)
        
        return query.order_by(
            cls.likes_count.desc(),
            cls.created_at.desc()
        ).limit(limit).all()

    def __repr__(self):
        return f'<Post {self.id} by {self.author_id}>'