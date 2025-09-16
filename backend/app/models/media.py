from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID, JSON, Integer
from sqlalchemy.sql import func
from app import db
import uuid

class Media(db.Model):
    __tablename__ = 'social_media'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('social_users.id'), nullable=False)
    storage_key = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    variants = Column(JSON, nullable=True)
    gramps_media_id = Column(String(100), nullable=True)
    gramps_url = Column(Text, nullable=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey('social_posts.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'storage_key': self.storage_key,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'variants': self.variants or {},
            'gramps_media_id': self.gramps_media_id,
            'gramps_url': self.gramps_url,
            'post_id': str(self.post_id) if self.post_id else None,
            'owner_id': str(self.owner_id),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_url(self, variant=None):
        if self.gramps_url:
            return self.gramps_url
        
        base_url = f"/api/media/{self.id}/file"
        if variant and self.variants and variant in self.variants:
            return f"{base_url}?variant={variant}"
        return base_url
    
    def get_thumbnail_url(self):
        return self.get_url('thumbnail')
    
    @classmethod
    def get_user_media(cls, owner_id, limit=20, offset=0):
        return cls.query.filter_by(owner_id=owner_id).order_by(
            cls.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    @classmethod
    def get_post_media(cls, post_id):
        return cls.query.filter_by(post_id=post_id).order_by(cls.created_at.asc()).all()
    
    def __repr__(self):
        return f'<Media {self.id}: {self.original_filename}>'