from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Post, Comment
from app import db

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/post/<int:post_id>/comments', methods=['GET'])
@jwt_required()
def get_post_comments(post_id):
    """Get all comments for a specific post"""
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return jsonify({'comments': [comment.to_dict() for comment in comments]}), 200

@comments_bp.route('/post/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """Create a new comment on a post"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify post exists
    post = Post.query.get_or_404(post_id)
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    if not data['content'].strip():
        return jsonify({'error': 'Content cannot be empty'}), 400
    
    comment = Comment(
        content=data['content'].strip(),
        author_id=current_user_id,
        post_id=post_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201

@comments_bp.route('/comments/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_comment(comment_id):
    """Get a specific comment"""
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.to_dict()), 200

@comments_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update a comment"""
    current_user_id = int(get_jwt_identity())
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    if not data['content'].strip():
        return jsonify({'error': 'Content cannot be empty'}), 400
    
    comment.content = data['content'].strip()
    db.session.commit()
    
    return jsonify(comment.to_dict()), 200

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment"""
    current_user_id = int(get_jwt_identity())
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200


