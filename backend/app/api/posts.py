from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Post, Like, Comment, Media, PostPrivacy
from app.models.notification import Notification
from app.services import GrampsMediaService
from app import db
import uuid

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
@jwt_required()
def get_posts():
    """Get all posts"""
    current_user_id = get_jwt_identity()
    posts = Post.query.filter_by(privacy=PostPrivacy.PUBLIC, is_deleted=False).order_by(Post.created_at.desc()).all()
    return jsonify({'posts': [post.to_dict(requesting_user=current_user_id) for post in posts]}), 200

@posts_bp.route('/popular', methods=['GET'])
@jwt_required()
def get_popular_posts():
    """Get popular posts ordered by likes"""
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    limit = request.args.get('limit', 20, type=int)
    window = request.args.get('window', None)  # '7d', '30d', or None for all time
    
    # Parse window parameter
    window_days = None
    if window == '7d':
        window_days = 7
    elif window == '30d':
        window_days = 30
    
    # Get popular posts
    posts = Post.get_popular_posts(
        limit=limit,
        window_days=window_days,
        user_id=current_user_id
    )
    
    return jsonify({
        'posts': [post.to_dict(requesting_user=current_user_id) for post in posts],
        'window': window,
        'limit': limit
    }), 200

@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new post"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'caption' not in data:
        return jsonify({'error': 'Caption is required'}), 400
    
    if not data['caption'].strip():
        return jsonify({'error': 'Caption cannot be empty'}), 400
    
    # Validate caption length
    if len(data['caption']) > 2200:
        return jsonify({'error': 'Caption must be 2200 characters or less'}), 400
    
    # Parse privacy setting
    privacy_str = data.get('privacy', 'public')
    try:
        privacy = PostPrivacy(privacy_str)
    except ValueError:
        return jsonify({'error': 'Invalid privacy setting'}), 400
    
    post = Post(
        caption=data['caption'].strip(),
        author_id=current_user_id,
        privacy=privacy,
        media=data.get('media', [])
    )
    
    # Extract hashtags and mentions from caption
    post.hashtags = post.extract_hashtags()
    post.mentions = post.extract_mentions()
    
    db.session.add(post)
    db.session.commit()
    
    # Get current user object for requesting_user
    current_user = User.query.get(current_user_id)
    return jsonify(post.to_dict(requesting_user=current_user)), 201

@posts_bp.route('/<post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    """Get a specific post"""
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'error': 'Invalid post ID format'}), 400
    
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_uuid)
    
    # Check if user can view this post
    if not post.can_view(current_user_id):
        return jsonify({'error': 'Post not found or access denied'}), 404
    
    return jsonify(post.to_dict(requesting_user=current_user_id)), 200

@posts_bp.route('/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """Update a post"""
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'error': 'Invalid post ID format'}), 400
    
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_uuid)
    
    if post.author_id != current_user_id:
        return jsonify({'error': 'You can only edit your own posts'}), 403
    
    data = request.get_json()
    
    if 'caption' in data:
        if not data['caption'].strip():
            return jsonify({'error': 'Caption cannot be empty'}), 400
        if len(data['caption']) > 2200:
            return jsonify({'error': 'Caption must be 2200 characters or less'}), 400
        post.caption = data['caption'].strip()
        post.is_edited = True
        post.edit_count += 1
        post.update_hashtags_and_mentions()
    
    if 'privacy' in data:
        try:
            post.privacy = PostPrivacy(data['privacy'])
        except ValueError:
            return jsonify({'error': 'Invalid privacy setting'}), 400
    
    if 'media' in data:
        post.media = data['media']
    
    db.session.commit()
    return jsonify(post.to_dict(requesting_user=current_user_id)), 200

@posts_bp.route('/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Delete a post (soft delete)"""
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'error': 'Invalid post ID format'}), 400
    
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_uuid)
    
    if post.author_id != current_user_id:
        return jsonify({'error': 'You can only delete your own posts'}), 403
    
    # Soft delete
    post.is_deleted = True
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

@posts_bp.route('/<post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """Like or unlike a post"""
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'error': 'Invalid post ID format'}), 400
    
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_uuid)
    
    # Check if user can view this post
    if not post.can_view(current_user_id):
        return jsonify({'error': 'Post not found or access denied'}), 404
    
    # Toggle like using the model method
    is_liked, action = Like.toggle_like(current_user_id, post_uuid)
    
    db.session.commit()
    
    # Create notification for the post author (if liked)
    if is_liked and post.author_id != current_user_id:
        Notification.create_notification(
            user_id=post.author_id,
            notification_type='like',
            actor_id=current_user_id,
            target_id=post_uuid,
            payload={'post_id': str(post_uuid)}
        )
        db.session.commit()
    
    return jsonify({
        'message': f'Post {action} successfully',
        'is_liked': is_liked,
        'likes_count': post.likes_count
    }), 200
