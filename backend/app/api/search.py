from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.post import Post
from app.models.follow import Follow
from app.models.friend import Friend
from sqlalchemy import or_, and_, func

search_bp = Blueprint('search', __name__)

@search_bp.route('/users', methods=['GET'])
@jwt_required()
def search_users():
    """Search users by name, username, or email"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'relevance')  # relevance, followers, created_at
    
    if not query or len(query.strip()) < 2:
        return jsonify({'error': 'Query must be at least 2 characters long'}), 400
    
    # Base query
    search_query = User.query.filter(
        or_(
            User.username.contains(query),
            User.first_name.contains(query),
            User.last_name.contains(query),
            User.email.contains(query)
        )
    ).filter_by(is_active=True)
    
    # Apply sorting
    if sort_by == 'followers':
        # Count followers for each user
        search_query = search_query.outerjoin(Follow, Follow.followed_id == User.id).group_by(User.id).order_by(func.count(Follow.id).desc())
    elif sort_by == 'created_at':
        search_query = search_query.order_by(User.created_at.desc())
    else:  # relevance
        # Simple relevance: exact matches first, then partial matches
        search_query = search_query.order_by(
            func.case(
                (User.username == query, 1),
                (User.first_name == query, 2),
                (User.last_name == query, 3),
                else_=4
            )
        )
    
    users = search_query.paginate(page=page, per_page=per_page, error_out=False)
    
    users_data = []
    for user in users.items:
        user_dict = user.to_dict()
        # Add follower count
        user_dict['followers_count'] = Follow.query.filter_by(followed_id=user.id).count()
        users_data.append(user_dict)
    
    return jsonify({
        'users': users_data,
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200

@search_bp.route('/posts', methods=['GET'])
@jwt_required()
def search_posts():
    """Search posts by content, hashtags, or author"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'relevance')  # relevance, likes, comments, created_at
    hashtag = request.args.get('hashtag', '')
    author_id = request.args.get('author_id', type=int)
    
    current_user_id = get_jwt_identity()
    
    # Base query
    search_query = Post.query.filter_by(is_public=True)
    
    # Apply search filters
    if query:
        search_query = search_query.filter(Post.content.contains(query))
    
    if hashtag:
        search_query = search_query.filter(Post.hashtags.contains([hashtag]))
    
    if author_id:
        search_query = search_query.filter(Post.author_id == author_id)
    
    # Apply sorting
    if sort_by == 'likes':
        search_query = search_query.outerjoin(Post.likes).group_by(Post.id).order_by(func.count(Post.likes).desc())
    elif sort_by == 'comments':
        search_query = search_query.outerjoin(Post.comments).group_by(Post.id).order_by(func.count(Post.comments).desc())
    elif sort_by == 'created_at':
        search_query = search_query.order_by(Post.created_at.desc())
    else:  # relevance
        search_query = search_query.order_by(Post.created_at.desc())
    
    posts = search_query.paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        # Check if current user can view this post
        if post.can_view(current_user_id):
            posts_data.append(post.to_dict())
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    }), 200

@search_bp.route('/hashtags', methods=['GET'])
@jwt_required()
def search_hashtags():
    """Search hashtags"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not query or len(query.strip()) < 1:
        return jsonify({'error': 'Query must be at least 1 character long'}), 400
    
    # Get all posts with hashtags
    posts_with_hashtags = Post.query.filter(Post.hashtags.isnot(None)).all()
    
    # Extract and count hashtags
    hashtag_counts = {}
    for post in posts_with_hashtags:
        if post.hashtags:
            for hashtag in post.hashtags:
                if query.lower() in hashtag.lower():
                    hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
    
    # Sort by count and apply pagination
    sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_hashtags = sorted_hashtags[start_idx:end_idx]
    
    hashtags_data = [
        {'hashtag': hashtag, 'count': count}
        for hashtag, count in paginated_hashtags
    ]
    
    total = len(sorted_hashtags)
    pages = (total + per_page - 1) // per_page
    
    return jsonify({
        'hashtags': hashtags_data,
        'total': total,
        'pages': pages,
        'current_page': page
    }), 200

@search_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_search_suggestions():
    """Get search suggestions based on query"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query or len(query.strip()) < 2:
        return jsonify({'suggestions': []}), 200
    
    suggestions = []
    
    # User suggestions
    users = User.query.filter(
        or_(
            User.username.contains(query),
            User.first_name.contains(query),
            User.last_name.contains(query)
        )
    ).filter_by(is_active=True).limit(limit).all()
    
    for user in users:
        suggestions.append({
            'type': 'user',
            'id': user.id,
            'title': user.username or f"{user.first_name} {user.last_name}".strip(),
            'subtitle': user.first_name and user.last_name and user.username or '',
            'avatar': user.avatar_url or user.google_picture
        })
    
    # Hashtag suggestions
    posts_with_hashtags = Post.query.filter(Post.hashtags.isnot(None)).all()
    hashtag_counts = {}
    
    for post in posts_with_hashtags:
        if post.hashtags:
            for hashtag in post.hashtags:
                if query.lower() in hashtag.lower():
                    hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
    
    # Add top hashtags to suggestions
    sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    for hashtag, count in sorted_hashtags:
        suggestions.append({
            'type': 'hashtag',
            'id': hashtag,
            'title': f"#{hashtag}",
            'subtitle': f"{count} posts",
            'avatar': None
        })
    
    return jsonify({'suggestions': suggestions}), 200

@search_bp.route('/trending', methods=['GET'])
@jwt_required()
def get_trending():
    """Get trending hashtags and posts"""
    limit = request.args.get('limit', 10, type=int)
    
    # Get trending hashtags (most used in last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_posts = Post.query.filter(Post.created_at >= week_ago).all()
    hashtag_counts = {}
    
    for post in recent_posts:
        if post.hashtags:
            for hashtag in post.hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
    
    trending_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    # Get trending posts (most liked in last 7 days)
    trending_posts = Post.query.filter(Post.created_at >= week_ago).all()
    post_scores = []
    
    for post in trending_posts:
        score = post.likes.count() + (post.comments.count() * 2)  # Comments worth more than likes
        post_scores.append((post, score))
    
    trending_posts_sorted = sorted(post_scores, key=lambda x: x[1], reverse=True)[:limit]
    
    return jsonify({
        'trending_hashtags': [
            {'hashtag': hashtag, 'count': count}
            for hashtag, count in trending_hashtags
        ],
        'trending_posts': [post.to_dict() for post, score in trending_posts_sorted]
    }), 200




