from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class Media(db.Model):
    __tablename__ = 'social_media'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    gramps_media_id = Column(String(100), nullable=True)  # ID в Gramps Web API
    gramps_url = Column(Text, nullable=True)  # URL в Gramps Web API
    post_id = Column(Integer, ForeignKey('social_posts.id'), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('social_users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    uploader = relationship('User', backref='uploaded_media')
    
    def to_dict(self):
        """Convert media to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'gramps_media_id': self.gramps_media_id,
            'gramps_url': self.gramps_url,
            'post_id': self.post_id,
            'uploaded_by': self.uploaded_by,
            'uploader': self.uploader.to_dict() if self.uploader else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Media {self.id}: {self.filename}>'


