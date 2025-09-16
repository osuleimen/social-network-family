from sqlalchemy import Column, DateTime, ForeignKey, Text, String, Enum, UUID, JSON
from sqlalchemy.sql import func
from app import db
import uuid
import enum

class ReportStatus(enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class ReportReason(enum.Enum):
    SPAM = "spam"
    HATE_SPEECH = "hate_speech"
    NSFW = "nsfw"
    HARASSMENT = "harassment"
    IMPERSONATION = "impersonation"
    OTHER = "other"

class ReportTargetType(enum.Enum):
    USER = "user"
    POST = "post"
    COMMENT = "comment"
    MEDIA = "media"

class Report(db.Model):
    __tablename__ = 'social_reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    target_type = Column(Enum(ReportTargetType), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    reason = Column(Enum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=True)
    ai_flags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    action_taken = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'reporter_id': str(self.reporter_id),
            'target_type': self.target_type.value,
            'target_id': str(self.target_id),
            'reason': self.reason.value,
            'description': self.description,
            'status': self.status.value,
            'assigned_to': str(self.assigned_to) if self.assigned_to else None,
            'ai_flags': self.ai_flags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'action_taken': self.action_taken
        }
    
    @classmethod
    def create_report(cls, reporter_id, target_type, target_id, reason, description=None, ai_flags=None):
        report = cls(
            reporter_id=reporter_id,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            description=description,
            ai_flags=ai_flags
        )
        db.session.add(report)
        return report
    
    def __repr__(self):
        return f'<Report {self.id} - {self.target_type.value}:{self.target_id}>'