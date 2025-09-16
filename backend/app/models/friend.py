from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, UUID, Enum
from sqlalchemy.sql import func
from app import db
import uuid
import enum

class FriendStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Friend(db.Model):
    __tablename__ = 'social_friends'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    requestee_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    status = Column(Enum(FriendStatus), default=FriendStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (UniqueConstraint('requester_id', 'requestee_id', name='unique_friendship'),)
    
    def to_dict(self):
        """Convert friend to dictionary"""
        return {
            'id': str(self.id),
            'requester_id': str(self.requester_id),
            'requestee_id': str(self.requestee_id),
            'status': self.status.value if self.status else 'pending',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None
        }
    
    @classmethod
    def send_friend_request(cls, requester_id, requestee_id):
        """Send a friend request"""
        existing = cls.query.filter_by(
            requester_id=requester_id, 
            requestee_id=requestee_id
        ).first()
        
        if existing:
            return False, "Request already exists"
        
        reverse = cls.query.filter_by(
            requester_id=requestee_id, 
            requestee_id=requester_id
        ).first()
        
        if reverse:
            return False, "Reverse request already exists"
        
        friend_request = cls(
            requester_id=requester_id,
            requestee_id=requestee_id,
            status=FriendStatus.PENDING
        )
        db.session.add(friend_request)
        return True, "Friend request sent"
    
    @classmethod
    def accept_friend_request(cls, request_id):
        """Accept a friend request"""
        friend_request = cls.query.get(request_id)
        if friend_request and friend_request.status == FriendStatus.PENDING:
            friend_request.status = FriendStatus.ACCEPTED
            friend_request.accepted_at = func.now()
            return True
        return False
    
    @classmethod
    def reject_friend_request(cls, request_id):
        """Reject a friend request"""
        friend_request = cls.query.get(request_id)
        if friend_request and friend_request.status == FriendStatus.PENDING:
            friend_request.status = FriendStatus.REJECTED
            return True
        return False
    
    @classmethod
    def remove_friend(cls, user1_id, user2_id):
        """Remove friendship between two users"""
        friendship = cls.query.filter(
            ((cls.requester_id == user1_id) & (cls.requestee_id == user2_id)) |
            ((cls.requester_id == user2_id) & (cls.requestee_id == user1_id))
        ).filter_by(status=FriendStatus.ACCEPTED).first()
        
        if friendship:
            db.session.delete(friendship)
            return True
        return False
    
    @classmethod
    def are_friends(cls, user1_id, user2_id):
        """Check if two users are friends"""
        return cls.query.filter(
            ((cls.requester_id == user1_id) & (cls.requestee_id == user2_id)) |
            ((cls.requester_id == user2_id) & (cls.requestee_id == user1_id))
        ).filter_by(status=FriendStatus.ACCEPTED).first() is not None
    
    @classmethod
    def get_friends(cls, user_id):
        """Get all friends of a user"""
        friends = cls.query.filter(
            ((cls.requester_id == user_id) | (cls.requestee_id == user_id))
        ).filter_by(status=FriendStatus.ACCEPTED).all()
        
        friend_ids = []
        for friend in friends:
            if friend.requester_id == user_id:
                friend_ids.append(friend.requestee_id)
            else:
                friend_ids.append(friend.requester_id)
        
        return friend_ids
    
    @classmethod
    def get_pending_requests(cls, user_id):
        """Get pending friend requests for a user"""
        return cls.query.filter_by(requestee_id=user_id, status=FriendStatus.PENDING).all()
    
    @classmethod
    def get_sent_requests(cls, user_id):
        """Get sent friend requests by a user"""
        return cls.query.filter_by(requester_id=user_id, status=FriendStatus.PENDING).all()
    
    def __repr__(self):
        return f'<Friend {self.requester_id} -> {self.requestee_id} ({self.status.value})>'