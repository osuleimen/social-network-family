from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Post, Follow
from sqlalchemy import desc, or_

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/', methods=['GET'])
@jwt_required()
def get_feed():
    """Get user's feed (posts from followed users and own posts)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get IDs of users that current user is following
        following_ids = [follow.followed_id for follow in user.following.all()]
        following_ids.append(current_user_id)  # Include own posts
        
        # Query posts from followed users and own posts
        posts = Post.query.filter(
            Post.author_id.in_(following_ids),
            Post.is_public == True
        ).order_by(desc(Post.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'total': posts.total,
            'pages': posts.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get feed'}), 500

@feed_bp.route('/explore', methods=['GET'])
@jwt_required()
def get_explore():
    """Get explore feed (public posts from all users)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Query all public posts
        posts = Post.query.filter(
            Post.is_public == True
        ).order_by(desc(Post.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'total': posts.total,
            'pages': posts.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get explore feed'}), 500

@feed_bp.route('/search', methods=['GET'])
@jwt_required()
def search_posts():
    """Search posts by content"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Search in post content
        posts = Post.query.filter(
            Post.is_public == True,
            Post.content.ilike(f'%{query}%')
        ).order_by(desc(Post.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'total': posts.total,
            'pages': posts.pages,
            'current_page': page,
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to search posts'}), 500
