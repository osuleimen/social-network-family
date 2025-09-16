from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.post import Post, PostPrivacy
from app.models.follow import Follow
from app.models.friend import Friend
from app.models.like import Like
from sqlalchemy import or_, and_, func, desc
from datetime import datetime, timedelta
import uuid

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/home', methods=['GET'])
@jwt_required()
def get_home_feed():
    """Get home feed for current user (posts from followed users)"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'recent')  # recent, popular, friends
    
    # Get users that current user is following
    following_ids = db.session.query(Follow.followed_id).filter_by(follower_id=current_user_id).subquery()
    
    # Base query for posts from followed users
    query = Post.query.filter(
        or_(
            Post.author_id.in_(following_ids),
            Post.author_id == current_user_id  # Include user's own posts
        )
    ).filter_by(privacy=PostPrivacy.PUBLIC, is_deleted=False)
    
    # Apply sorting
    if sort_by == 'popular':
        # Sort by engagement (likes + comments) - use denormalized counters
        query = query.order_by(desc(Post.likes_count + Post.comments_count))
    elif sort_by == 'friends':
        # Get friends
        friends_query = db.session.query(Friend.user2_id).filter(
            and_(Friend.user1_id == current_user_id, Friend.status == 'accepted')
        ).union(
            db.session.query(Friend.user1_id).filter(
                and_(Friend.user2_id == current_user_id, Friend.status == 'accepted')
            )
        ).subquery()
        
        # Prioritize posts from friends
        query = query.order_by(
            desc(func.case(
                (Post.author_id.in_(friends_query), 1),
                else_=0
            )),
            desc(Post.created_at)
        )
    else:  # recent
        query = query.order_by(desc(Post.created_at))
    
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        # Check if user can view this post
        if post.can_view(current_user_id):
            post_dict = post.to_dict()
            
            # Add user's like status
            user_like = Like.query.filter_by(
                user_id=current_user_id,
                post_id=post.id
            ).first()
            post_dict['user_liked'] = user_like is not None
            
            posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    }), 200

@feed_bp.route('/popular', methods=['GET'])
def get_popular_feed():
    """Get popular posts (public endpoint)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    window_days = request.args.get('window_days', type=int)  # Optional time window
    
    # Get popular posts using the model method
    posts = Post.get_popular_posts(limit=per_page, window_days=window_days)
    
    return jsonify({
        'success': True,
        'posts': [post.to_dict() for post in posts],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': len(posts)
        }
    }), 200

@feed_bp.route('/explore', methods=['GET'])
@jwt_required()
def get_explore_feed():
    """Get explore feed (popular posts from all users)"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category', 'all')  # all, trending, recent
    
    # Base query for public posts
    query = Post.query.filter_by(privacy=PostPrivacy.PUBLIC, is_deleted=False)
    
    # Apply category filters
    if category == 'trending':
        # Posts with high engagement in last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        query = query.filter(Post.created_at >= yesterday)
        query = query.order_by(desc(Post.likes_count + Post.comments_count))
    elif category == 'recent':
        query = query.order_by(desc(Post.created_at))
    else:  # all
        # Mix of recent and popular - use denormalized counters
        query = query.order_by(desc(Post.likes_count + Post.comments_count), desc(Post.created_at))
    
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        # Check if user can view this post
        if post.can_view(current_user_id):
            post_dict = post.to_dict()
            
            # Add user's like status
            user_like = Like.query.filter_by(
                user_id=current_user_id,
                post_id=post.id
            ).first()
            post_dict['user_liked'] = user_like is not None
            
            posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    }), 200

@feed_bp.route('/friends', methods=['GET'])
@jwt_required()
def get_friends_feed():
    """Get feed with posts from friends only"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get friends
    friends_query = db.session.query(Friend.user2_id).filter(
        and_(Friend.user1_id == current_user_id, Friend.status == 'accepted')
    ).union(
        db.session.query(Friend.user1_id).filter(
            and_(Friend.user2_id == current_user_id, Friend.status == 'accepted')
        )
    ).subquery()
    
    # Get posts from friends
    query = Post.query.filter(
        or_(
            Post.author_id.in_(friends_query),
            Post.author_id == current_user_id  # Include user's own posts
        )
    ).filter_by(privacy=PostPrivacy.PUBLIC, is_deleted=False).order_by(desc(Post.created_at))
    
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        post_dict = post.to_dict()
        
        # Add user's like status
        user_like = Like.query.filter_by(
            user_id=current_user_id,
            post_id=post.id
        ).first()
        post_dict['user_liked'] = user_like is not None
        
        posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    }), 200

@feed_bp.route('/hashtag/<hashtag>', methods=['GET'])
@jwt_required()
def get_hashtag_feed(hashtag):
    """Get feed for a specific hashtag"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'recent')  # recent, popular
    
    # Get posts with the hashtag
    query = Post.query.filter(
        Post.hashtags.contains([hashtag])
    ).filter_by(privacy=PostPrivacy.PUBLIC, is_deleted=False)
    
    # Apply sorting
    if sort_by == 'popular':
        query = query.order_by(desc(Post.likes_count + Post.comments_count))
    else:  # recent
        query = query.order_by(desc(Post.created_at))
    
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        # Check if user can view this post
        if post.can_view(current_user_id):
            post_dict = post.to_dict()
            
            # Add user's like status
            user_like = Like.query.filter_by(
                user_id=current_user_id,
                post_id=post.id
            ).first()
            post_dict['user_liked'] = user_like is not None
            
            posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page,
        'hashtag': hashtag
    }), 200

@feed_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_feed(user_id):
    """Get feed for a specific user"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Convert string UUID to UUID object
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    # Check if user exists
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get posts from the user
    query = Post.query.filter_by(author_id=user_uuid)
    
    # Apply privacy filters
    if current_user_id != str(user_uuid):
        # For other users, only show public posts or posts user can view
        query = query.filter(
            Post.privacy == PostPrivacy.PUBLIC,
            Post.is_deleted == False
        )
    
    posts = query.order_by(desc(Post.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts_data = []
    for post in posts.items:
        # Check if user can view this post
        if post.can_view(current_user_id):
            post_dict = post.to_dict()
            
            # Add user's like status
            user_like = Like.query.filter_by(
                user_id=current_user_id,
                post_id=post.id
            ).first()
            post_dict['user_liked'] = user_like is not None
            
            posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page,
        'user': user.to_dict()
    }), 200