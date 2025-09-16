from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Boolean, JSON
from sqlalchemy.sql import func
from app import db
import uuid

class Notification(db.Model):
    __tablename__ = 'social_notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=True)
    target_id = Column(UUID(as_uuid=True), nullable=True)
    type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'actor_id': str(self.actor_id) if self.actor_id else None,
            'target_id': str(self.target_id) if self.target_id else None,
            'type': self.type,
            'payload': self.payload or {},
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_notification(cls, user_id, notification_type, actor_id=None, target_id=None, payload=None):
        """Create a new notification"""
        notification = cls(
            user_id=user_id,
            type=notification_type,
            actor_id=actor_id,
            target_id=target_id,
            payload=payload or {}
        )
        db.session.add(notification)
        return notification
    
    @classmethod
    def get_user_notifications(cls, user_id, limit=20, offset=0):
        """Get notifications for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(
            cls.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    @classmethod
    def get_unread_count(cls, user_id):
        """Get unread notification count for user"""
        return cls.query.filter_by(user_id=user_id, read=False).count()
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
    
    @classmethod
    def mark_all_as_read(cls, user_id):
        """Mark all notifications as read for user"""
        cls.query.filter_by(user_id=user_id, read=False).update({'read': True})
    
    def __repr__(self):
        return f'<Notification {self.type} for {self.user_id}>'