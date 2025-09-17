from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import User, Post, Media
from app.services import GrampsMediaService
from app import db
import logging

logger = logging.getLogger(__name__)

media_bp = Blueprint('media', __name__)

# Configure allowed file types and max file size
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@media_bp.route('/posts/<post_id>/media', methods=['POST'])
@jwt_required()
def upload_media_to_post(post_id):
    """Upload media files to a post"""
    current_user_id = get_jwt_identity()
    
    # Verify post exists
    post = Post.query.get_or_404(post_id)
    
    # Check if user can upload to this post (post author only)
    if str(post.author_id) != current_user_id:
        return jsonify({'error': 'Unauthorized - only post author can upload media'}), 403
    
    # Check if files were uploaded
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No files selected'}), 400
    
    uploaded_media = []
    errors = []
    gramps_service = GrampsMediaService()
    
    for file in files:
        if file and file.filename:
            # Validate file
            if not allowed_file(file.filename):
                errors.append(f"File '{file.filename}' has unsupported format")
                continue
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f"File '{file.filename}' is too large (max {MAX_FILE_SIZE // (1024*1024)}MB)")
                continue
            
            try:
                # Read file data
                file_data = file.read()
                file.seek(0)  # Reset for potential re-reading
                
                # Upload to Gramps
                upload_result = gramps_service.upload_media_file(
                    file_data=file_data,
                    filename=file.filename,
                    mime_type=file.content_type or 'application/octet-stream'
                )
                
                if upload_result:
                    # Save media info to database
                    media = Media(
                        storage_key=upload_result['filename'],
                        original_filename=upload_result['original_filename'],
                        mime_type=upload_result['mime_type'],
                        file_size=upload_result['file_size'],
                        gramps_media_id=upload_result['gramps_media_id'],
                        gramps_url=upload_result['gramps_url'],
                        post_id=post_id,
                        owner_id=current_user_id
                    )
                    
                    db.session.add(media)
                    db.session.commit()
                    
                    uploaded_media.append(media.to_dict())
                    logger.info(f"Successfully uploaded media for post {post_id}: {file.filename}")
                else:
                    errors.append(f"Failed to upload '{file.filename}' to Gramps")
                    
            except Exception as e:
                logger.error(f"Error uploading file '{file.filename}': {str(e)}")
                errors.append(f"Error uploading '{file.filename}': {str(e)}")
    
    # Prepare response
    response_data = {
        'uploaded_media': uploaded_media,
        'upload_count': len(uploaded_media)
    }
    
    if errors:
        response_data['errors'] = errors
    
    status_code = 201 if uploaded_media else 400
    return jsonify(response_data), status_code

@media_bp.route('/posts/<post_id>/media', methods=['GET'])
@jwt_required()
def get_post_media(post_id):
    """Get all media files for a post"""
    post = Post.query.get_or_404(post_id)
    media_files = Media.query.filter_by(post_id=post_id).all()
    
    return jsonify({
        'media': [media.to_dict() for media in media_files],
        'count': len(media_files)
    }), 200

@media_bp.route('/media/<int:media_id>', methods=['GET'])
@jwt_required()
def get_media(media_id):
    """Get specific media file info"""
    media = Media.query.get_or_404(media_id)
    return jsonify(media.to_dict()), 200

@media_bp.route('/media/<int:media_id>', methods=['DELETE'])
@jwt_required()
def delete_media(media_id):
    """Delete a media file"""
    current_user_id = get_jwt_identity()
    media = Media.query.get_or_404(media_id)
    
    # Check if user can delete this media (uploader or post author only)
    post = Post.query.get(media.post_id)
    if str(media.owner_id) != current_user_id and str(post.author_id) != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete from local storage
    gramps_service = GrampsMediaService()
    gramps_deleted = gramps_service.delete_media_file(media.storage_key)
    
    if not gramps_deleted:
        logger.warning(f"Failed to delete media from local storage: {media.storage_key}")
        # Continue with database deletion anyway
    
    # Delete from database
    db.session.delete(media)
    db.session.commit()
    
    return jsonify({'message': 'Media deleted successfully'}), 200

@media_bp.route('/media/<int:media_id>/url', methods=['GET'])
@jwt_required()
def get_media_url(media_id):
    """Get the direct URL for accessing a media file"""
    media = Media.query.get_or_404(media_id)
    
    if media.gramps_url:
        return jsonify({
            'url': media.gramps_url,
            'filename': media.original_filename,
            'mime_type': media.mime_type
        }), 200
    else:
        return jsonify({'error': 'Media URL not available'}), 404

@media_bp.route('/uploads/<filename>', methods=['GET'])
def serve_uploaded_file(filename):
    """Serve uploaded media files"""
    from flask import send_from_directory
    import os
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(uploads_dir, filename)


