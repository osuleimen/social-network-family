from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.follow import Follow, FollowStatus
from app.models.notification import Notification
from datetime import datetime
import uuid

follows_bp = Blueprint('follows', __name__)

@follows_bp.route('/follow/<user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    """Follow a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    if current_user_id == str(user_uuid):
        return jsonify({'error': 'Cannot follow yourself'}), 400
    
    # Check if user exists
    user_to_follow = User.query.get(user_uuid)
    if not user_to_follow:
        return jsonify({'error': 'User not found'}), 404
    
    # Use the model method to toggle follow
    is_following, action = Follow.toggle_follow(current_user_id, user_uuid)
    
    if is_following:
        # Create notification
        Notification.create_notification(
            user_id=user_to_follow.id,
            notification_type='follow',
            actor_id=current_user_id,
            target_id=user_to_follow.id,
            payload={'action': action}
        )
    
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully {action} user',
        'is_following': is_following,
        'action': action
    }), 200

@follows_bp.route('/unfollow/<user_id>', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    """Unfollow a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    # Use the model method to toggle follow (this will unfollow if already following)
    is_following, action = Follow.toggle_follow(current_user_id, user_uuid)
    
    if not is_following:
        db.session.commit()
        return jsonify({'message': 'Successfully unfollowed user'}), 200
    else:
        return jsonify({'error': 'Not following this user'}), 404

@follows_bp.route('/followers/<int:user_id>', methods=['GET'])
@jwt_required()
def get_followers(user_id):
    """Get followers of a user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    followers_query = Follow.query.filter_by(followed_id=user_id)
    followers = followers_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    follower_users = []
    for follow in followers.items:
        user = User.query.get(follow.follower_id)
        if user:
            follower_users.append({
                'user': user.to_dict(),
                'followed_at': follow.created_at.isoformat()
            })
    
    return jsonify({
        'followers': follower_users,
        'total': followers.total,
        'pages': followers.pages,
        'current_page': page
    }), 200

@follows_bp.route('/following/<int:user_id>', methods=['GET'])
@jwt_required()
def get_following(user_id):
    """Get users that a user is following"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    following_query = Follow.query.filter_by(follower_id=user_id)
    following = following_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    following_users = []
    for follow in following.items:
        user = User.query.get(follow.followed_id)
        if user:
            following_users.append({
                'user': user.to_dict(),
                'followed_at': follow.created_at.isoformat()
            })
    
    return jsonify({
        'following': following_users,
        'total': following.total,
        'pages': following.pages,
        'current_page': page
    }), 200

@follows_bp.route('/follow-status/<int:user_id>', methods=['GET'])
@jwt_required()
def get_follow_status(user_id):
    """Check if current user follows another user"""
    current_user_id = get_jwt_identity()
    
    follow = Follow.query.filter_by(
        follower_id=current_user_id,
        followed_id=user_id
    ).first()
    
    return jsonify({
        'is_following': follow is not None,
        'followed_at': follow.created_at.isoformat() if follow else None
    }), 200

@follows_bp.route('/followers-count/<int:user_id>', methods=['GET'])
def get_followers_count(user_id):
    """Get followers count for a user"""
    count = Follow.query.filter_by(followed_id=user_id).count()
    return jsonify({'followers_count': count}), 200

@follows_bp.route('/following-count/<user_id>', methods=['GET'])
def get_following_count(user_id):
    """Get following count for a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    count = Follow.query.filter_by(follower_id=user_uuid, status=FollowStatus.ACCEPTED).count()
    return jsonify({'following_count': count}), 200

@follows_bp.route('/follow-requests', methods=['GET'])
@jwt_required()
def get_follow_requests():
    """Get pending follow requests for current user"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get pending follow requests
    requests = Follow.get_followers(current_user_id, status=FollowStatus.PENDING)
    
    # Paginate manually
    start = (page - 1) * per_page
    end = start + per_page
    paginated_requests = requests[start:end]
    
    request_data = []
    for follow in paginated_requests:
        follower = User.query.get(follow.follower_id)
        if follower:
            request_data.append({
                'follow_id': str(follow.id),
                'follower': follower.to_dict(),
                'requested_at': follow.created_at.isoformat()
            })
    
    return jsonify({
        'requests': request_data,
        'total': len(requests),
        'page': page,
        'per_page': per_page
    }), 200

@follows_bp.route('/follow-requests/<request_id>/accept', methods=['POST'])
@jwt_required()
def accept_follow_request(request_id):
    """Accept a follow request"""
    try:
        request_uuid = uuid.UUID(request_id)
    except ValueError:
        return jsonify({'error': 'Invalid request ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    # Find the follow request
    follow_request = Follow.query.get(request_uuid)
    if not follow_request:
        return jsonify({'error': 'Follow request not found'}), 404
    
    # Check if the request is for the current user
    if follow_request.followed_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Accept the request
    if Follow.accept_follow_request(request_uuid):
        db.session.commit()
        return jsonify({'message': 'Follow request accepted'}), 200
    else:
        return jsonify({'error': 'Failed to accept follow request'}), 400

@follows_bp.route('/follow-requests/<request_id>/decline', methods=['POST'])
@jwt_required()
def decline_follow_request(request_id):
    """Decline a follow request"""
    try:
        request_uuid = uuid.UUID(request_id)
    except ValueError:
        return jsonify({'error': 'Invalid request ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    # Find the follow request
    follow_request = Follow.query.get(request_uuid)
    if not follow_request:
        return jsonify({'error': 'Follow request not found'}), 404
    
    # Check if the request is for the current user
    if follow_request.followed_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Decline the request
    if Follow.decline_follow_request(request_uuid):
        db.session.commit()
        return jsonify({'message': 'Follow request declined'}), 200
    else:
        return jsonify({'error': 'Failed to decline follow request'}), 400


