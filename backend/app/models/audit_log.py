from sqlalchemy import Column, DateTime, ForeignKey, Text, String, JSON, UUID
from sqlalchemy.sql import func
from app import db
import uuid

class AuditLog(db.Model):
    __tablename__ = 'social_audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(UUID(as_uuid=True), nullable=True)
    action_metadata = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'actor_id': str(self.actor_id),
            'action': self.action,
            'target_type': self.target_type,
            'target_id': str(self.target_id) if self.target_id else None,
            'action_metadata': self.action_metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def log_action(cls, actor_id, action, target_type=None, target_id=None, action_metadata=None,
                   ip_address=None, user_agent=None):
        audit_log = cls(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            action_metadata=action_metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(audit_log)
        return audit_log
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.actor_id}>'