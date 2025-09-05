from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Post, Like, Comment, Media
from app.services import GrampsMediaService
from app import db

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
@jwt_required()
def get_posts():
    """Get all posts"""
    posts = Post.query.filter_by(is_public=True).order_by(Post.created_at.desc()).all()
    return jsonify({'posts': [post.to_dict() for post in posts]}), 200

@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new post"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    if not data['content'].strip():
        return jsonify({'error': 'Content cannot be empty'}), 400
    
    post = Post(
        content=data['content'].strip(),
        author_id=current_user_id,
        is_public=data.get('is_public', True)
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201

@posts_bp.route('/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    """Get a specific post"""
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict()), 200

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """Update a post"""
    current_user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    if post.author_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if 'content' in data:
        if not data['content'].strip():
            return jsonify({'error': 'Content cannot be empty'}), 400
        post.content = data['content'].strip()
    if 'is_public' in data:
        post.is_public = data['is_public']
    
    db.session.commit()
    return jsonify(post.to_dict()), 200

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Delete a post"""
    current_user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    if post.author_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """Like or unlike a post"""
    current_user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    # Check if user already liked this post
    existing_like = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()
    
    if existing_like:
        # Unlike the post
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'message': 'Post unliked successfully'}), 200
    else:
        # Like the post
        like = Like(user_id=current_user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'message': 'Post liked successfully'}), 200
