from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Post, Comment, Like, Notification
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import desc

posts_bp = Blueprint('posts', __name__)

class CreatePostSchema(Schema):
    content = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    is_public = fields.Bool()

class UpdatePostSchema(Schema):
    content = fields.Str(validate=lambda x: len(x.strip()) > 0)
    is_public = fields.Bool()

class CreateCommentSchema(Schema):
    content = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    parent_id = fields.Int()

@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new post"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        schema = CreatePostSchema()
        data = schema.load(request.json)
        
        post = Post(
            content=data['content'],
            author_id=current_user_id,
            is_public=data.get('is_public', True)
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create post'}), 500

@posts_bp.route('/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    """Get specific post by ID"""
    try:
        post = Post.query.get_or_404(post_id)
        
        # Check if user can view this post
        current_user_id = get_jwt_identity()
        if not post.is_public and post.author_id != current_user_id:
            return jsonify({'error': 'Post not found'}), 404
        
        return jsonify({
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get post'}), 500

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """Update a post"""
    try:
        current_user_id = get_jwt_identity()
        post = Post.query.get_or_404(post_id)
        
        # Check if user owns this post
        if post.author_id != current_user_id:
            return jsonify({'error': 'Not authorized to update this post'}), 403
        
        schema = UpdatePostSchema()
        data = schema.load(request.json)
        
        for key, value in data.items():
            setattr(post, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Post updated successfully',
            'post': post.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update post'}), 500

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Delete a post"""
    try:
        current_user_id = get_jwt_identity()
        post = Post.query.get_or_404(post_id)
        
        # Check if user owns this post
        if post.author_id != current_user_id:
            return jsonify({'error': 'Not authorized to delete this post'}), 403
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete post'}), 500

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """Like a post"""
    try:
        current_user_id = get_jwt_identity()
        post = Post.query.get_or_404(post_id)
        
        # Check if already liked
        existing_like = Like.query.filter_by(
            user_id=current_user_id,
            post_id=post_id
        ).first()
        
        if existing_like:
            return jsonify({'error': 'Already liked this post'}), 400
        
        # Create like
        like = Like(user_id=current_user_id, post_id=post_id)
        db.session.add(like)
        
        # Create notification if not liking own post
        if post.author_id != current_user_id:
            notification = Notification(
                user_id=post.author_id,
                type='like',
                title='New Like',
                message=f'Someone liked your post',
                data={'post_id': post_id, 'user_id': current_user_id}
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({'message': 'Post liked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to like post'}), 500

@posts_bp.route('/<int:post_id>/unlike', methods=['POST'])
@jwt_required()
def unlike_post(post_id):
    """Unlike a post"""
    try:
        current_user_id = get_jwt_identity()
        
        like = Like.query.filter_by(
            user_id=current_user_id,
            post_id=post_id
        ).first()
        
        if not like:
            return jsonify({'error': 'Not liked this post'}), 400
        
        db.session.delete(like)
        db.session.commit()
        
        return jsonify({'message': 'Post unliked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to unlike post'}), 500

@posts_bp.route('/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """Create a comment on a post"""
    try:
        current_user_id = get_jwt_identity()
        post = Post.query.get_or_404(post_id)
        
        # Check if user can view this post
        if not post.is_public and post.author_id != current_user_id:
            return jsonify({'error': 'Post not found'}), 404
        
        schema = CreateCommentSchema()
        data = schema.load(request.json)
        
        comment = Comment(
            content=data['content'],
            author_id=current_user_id,
            post_id=post_id,
            parent_id=data.get('parent_id')
        )
        
        db.session.add(comment)
        
        # Create notification if not commenting on own post
        if post.author_id != current_user_id:
            notification = Notification(
                user_id=post.author_id,
                type='comment',
                title='New Comment',
                message=f'Someone commented on your post',
                data={'post_id': post_id, 'comment_id': comment.id, 'user_id': current_user_id}
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comment created successfully',
            'comment': comment.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create comment'}), 500

@posts_bp.route('/<int:post_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(post_id):
    """Get comments for a post"""
    try:
        post = Post.query.get_or_404(post_id)
        
        # Check if user can view this post
        current_user_id = get_jwt_identity()
        if not post.is_public and post.author_id != current_user_id:
            return jsonify({'error': 'Post not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        comments = Comment.query.filter_by(
            post_id=post_id,
            parent_id=None  # Only top-level comments
        ).order_by(desc(Comment.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments.items],
            'total': comments.total,
            'pages': comments.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get comments'}), 500
