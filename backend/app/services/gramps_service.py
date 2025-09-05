import requests
import os
import uuid
from werkzeug.utils import secure_filename
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GrampsMediaService:
    """Service for uploading and managing media files via Gramps Web API"""
    
    def __init__(self):
        self.base_url = os.environ.get('GRAMPS_BASE_URL', 'http://grampsweb:5000')
        self.api_key = os.environ.get('GRAMPS_API_KEY', '')
        self.session = requests.Session()
        
        # Set up authentication headers if API key is provided
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    def upload_media_file(self, file_data: bytes, filename: str, mime_type: str) -> Optional[Dict[str, Any]]:
        """
        Upload a media file to Gramps Web API
        
        Args:
            file_data: Binary file data
            filename: Original filename
            mime_type: MIME type of the file
            
        Returns:
            Dictionary with media information or None if failed
        """
        try:
            # Generate a unique filename to avoid conflicts
            safe_filename = secure_filename(filename)
            unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
            
            # For now, we'll store files locally and return a mock Gramps response
            # This allows us to test the media upload functionality
            # TODO: Implement actual Gramps Web API integration
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file locally
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Successfully saved media file locally: {unique_filename}")
            
            # Return mock Gramps response for now
            return {
                'gramps_media_id': str(uuid.uuid4()),  # Mock ID
                'gramps_url': f"https://my.ozimiz.org/api/uploads/{unique_filename}",  # Full URL for frontend
                'filename': unique_filename,
                'original_filename': filename,
                'mime_type': mime_type,
                'file_size': len(file_data)
            }
                
        except Exception as e:
            logger.error(f"Error uploading media file: {str(e)}")
            return None
    
    def get_media_url(self, gramps_media_id: str) -> Optional[str]:
        """
        Get the URL for accessing a media file from Gramps
        
        Args:
            gramps_media_id: Gramps media handle/ID
            
        Returns:
            URL string or None if not found
        """
        try:
            if not gramps_media_id:
                return None
                
            # For now, return local URL
            return f"/uploads/{gramps_media_id}"
            
        except Exception as e:
            logger.error(f"Error getting media URL: {str(e)}")
            return None
    
    def delete_media_file(self, filename: str) -> bool:
        """
        Delete a media file from local storage
        
        Args:
            filename: The filename to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not filename:
                return False
                
            # For now, try to delete local file
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            file_path = os.path.join(upload_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Successfully deleted local media file: {filename}")
                return True
            else:
                logger.warning(f"Local media file not found: {filename}")
                return True  # Consider it deleted if it doesn't exist
                
        except Exception as e:
            logger.error(f"Error deleting media file: {str(e)}")
            return False
    
    def get_media_info(self, gramps_media_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a media file from Gramps Web API
        
        Args:
            gramps_media_id: Gramps media handle/ID
            
        Returns:
            Dictionary with media information or None if not found
        """
        try:
            if not gramps_media_id:
                return None
                
            # For now, return mock info
            return {
                'handle': gramps_media_id,
                'filename': gramps_media_id,
                'mime_type': 'image/jpeg',  # Default
                'size': 0  # Default
            }
            
        except Exception as e:
            logger.error(f"Error getting media info: {str(e)}")
            return None


