from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.post import Post
from app.services.ai_service import ai_service
import os
import time
from werkzeug.utils import secure_filename

ai_bp = Blueprint('ai', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ai_bp.route('/generate-description', methods=['POST'])
@jwt_required()
def generate_description():
    """Generate description for a post based on image"""
    if not ai_service.is_available():
        return jsonify({'error': 'AI service is not available'}), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif, webp'}), 400
    
    # Get language preference
    language = request.form.get('language', 'ru')
    if language not in ['ru', 'en', 'kk']:
        language = 'ru'
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        file.save(filepath)
        
        # Generate description
        description = ai_service.generate_post_description(filepath, language)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        if description:
            return jsonify({
                'description': description,
                'language': language
            }), 200
        else:
            return jsonify({'error': 'Failed to generate description'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@ai_bp.route('/generate-hashtags', methods=['POST'])
@jwt_required()
def generate_hashtags():
    """Generate hashtags based on description"""
    if not ai_service.is_available():
        return jsonify({'error': 'AI service is not available'}), 503
    
    data = request.get_json()
    description = data.get('description', '')
    language = data.get('language', 'ru')
    
    if not description:
        return jsonify({'error': 'Description is required'}), 400
    
    if language not in ['ru', 'en', 'kk']:
        language = 'ru'
    
    try:
        hashtags = ai_service.generate_hashtags(description, language)
        
        return jsonify({
            'hashtags': hashtags,
            'language': language
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error generating hashtags: {str(e)}'}), 500

@ai_bp.route('/enhance-content', methods=['POST'])
@jwt_required()
def enhance_content():
    """Enhance post content with AI"""
    if not ai_service.is_available():
        return jsonify({'error': 'AI service is not available'}), 503
    
    data = request.get_json()
    content = data.get('content', '')
    language = data.get('language', 'ru')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    if language not in ['ru', 'en', 'kk']:
        language = 'ru'
    
    try:
        enhanced_content = ai_service.enhance_post_content(content, language)
        
        if enhanced_content:
            return jsonify({
                'enhanced_content': enhanced_content,
                'original_content': content,
                'language': language
            }), 200
        else:
            return jsonify({'error': 'Failed to enhance content'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error enhancing content: {str(e)}'}), 500

@ai_bp.route('/auto-generate-post', methods=['POST'])
@jwt_required()
def auto_generate_post():
    """Auto-generate complete post with description and hashtags"""
    if not ai_service.is_available():
        return jsonify({'error': 'AI service is not available'}), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif, webp'}), 400
    
    # Get language preference
    language = request.form.get('language', 'ru')
    if language not in ['ru', 'en', 'kk']:
        language = 'ru'
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        file.save(filepath)
        
        # Generate description
        description = ai_service.generate_post_description(filepath, language)
        
        # Generate hashtags
        hashtags = []
        if description:
            hashtags = ai_service.generate_hashtags(description, language)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'description': description or '',
            'hashtags': hashtags,
            'language': language
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@ai_bp.route('/status', methods=['GET'])
def get_ai_status():
    """Get AI service status"""
    return jsonify({
        'available': ai_service.is_available(),
        'service': 'Gemini AI'
    }), 200

@ai_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get supported languages for AI generation"""
    return jsonify({
        'languages': [
            {'code': 'ru', 'name': 'Русский'},
            {'code': 'en', 'name': 'English'},
            {'code': 'kk', 'name': 'Қазақша'}
        ]
    }), 200
