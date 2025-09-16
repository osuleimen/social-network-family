from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, UUID, Enum
from sqlalchemy.sql import func
from app import db
import uuid
import enum

class FollowStatus(enum.Enum):
    ACCEPTED = "accepted"
    PENDING = "pending"

class Follow(db.Model):
    __tablename__ = 'social_follows'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    followed_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    status = Column(Enum(FollowStatus), default=FollowStatus.ACCEPTED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)
    
    def to_dict(self):
        """Convert follow to dictionary"""
        return {
            'id': str(self.id),
            'follower_id': str(self.follower_id),
            'followed_id': str(self.followed_id),
            'status': self.status.value if self.status else 'accepted',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def toggle_follow(cls, follower_id, followed_id):
        """Toggle follow relationship (idempotent)"""
        existing_follow = cls.query.filter_by(
            follower_id=follower_id, 
            followed_id=followed_id
        ).first()
        
        if existing_follow:
            db.session.delete(existing_follow)
            return False, "unfollowed"
        else:
            from app.models.user import User
            target_user = User.query.get(followed_id)
            
            if target_user and target_user.private_account:
                new_follow = cls(
                    follower_id=follower_id, 
                    followed_id=followed_id,
                    status=FollowStatus.PENDING
                )
            else:
                new_follow = cls(
                    follower_id=follower_id, 
                    followed_id=followed_id,
                    status=FollowStatus.ACCEPTED
                )
            
            db.session.add(new_follow)
            return True, "followed" if new_follow.status == FollowStatus.ACCEPTED else "follow_requested"
    
    @classmethod
    def accept_follow_request(cls, follow_id):
        """Accept a pending follow request"""
        follow = cls.query.get(follow_id)
        if follow and follow.status == FollowStatus.PENDING:
            follow.status = FollowStatus.ACCEPTED
            return True
        return False
    
    @classmethod
    def decline_follow_request(cls, follow_id):
        """Decline a pending follow request"""
        follow = cls.query.get(follow_id)
        if follow and follow.status == FollowStatus.PENDING:
            db.session.delete(follow)
            return True
        return False
    
    @classmethod
    def get_followers(cls, user_id, status=None):
        """Get followers of a user"""
        query = cls.query.filter_by(followed_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.all()
    
    @classmethod
    def get_following(cls, user_id, status=None):
        """Get users that a user is following"""
        query = cls.query.filter_by(follower_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.all()
    
    @classmethod
    def is_following(cls, follower_id, followed_id):
        """Check if user is following another user"""
        follow = cls.query.filter_by(
            follower_id=follower_id, 
            followed_id=followed_id,
            status=FollowStatus.ACCEPTED
        ).first()
        return follow is not None
    
    def __repr__(self):
        return f'<Follow {self.follower_id} -> {self.followed_id} ({self.status.value})>'