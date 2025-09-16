from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.friend import Friend, FriendStatus
from app.models.notification import Notification
from datetime import datetime
import uuid

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/send-request/<user_id>', methods=['POST'])
@jwt_required()
def send_friend_request(user_id):
    """Send a friend request"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    if current_user_id == str(user_uuid):
        return jsonify({'error': 'Cannot send friend request to yourself'}), 400
    
    # Check if user exists
    user_to_friend = User.query.get(user_uuid)
    if not user_to_friend:
        return jsonify({'error': 'User not found'}), 404
    
    # Use the model method to send friend request
    success, message = Friend.send_friend_request(current_user_id, user_uuid)
    
    if success:
        # Create notification
        Notification.create_notification(
            user_id=user_to_friend.id,
            notification_type='friend_request',
            actor_id=current_user_id,
            target_id=user_to_friend.id,
            payload={'action': 'friend_request_sent'}
        )
        
        db.session.commit()
        return jsonify({'message': message}), 201
    else:
        return jsonify({'error': message}), 400

@friends_bp.route('/accept-request/<request_id>', methods=['POST'])
@jwt_required()
def accept_friend_request(request_id):
    """Accept a friend request"""
    try:
        request_uuid = uuid.UUID(request_id)
    except ValueError:
        return jsonify({'error': 'Invalid request ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    # Find friend request
    friend_request = Friend.query.get(request_uuid)
    if not friend_request:
        return jsonify({'error': 'Friend request not found'}), 404
    
    if friend_request.requestee_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Accept the request
    if Friend.accept_friend_request(request_uuid):
        # Create notification for the requester
        Notification.create_notification(
            user_id=friend_request.requester_id,
            notification_type='friend_accepted',
            actor_id=current_user_id,
            target_id=friend_request.requester_id,
            payload={'action': 'friend_request_accepted'}
        )
        
        db.session.commit()
        return jsonify({'message': 'Friend request accepted'}), 200
    else:
        return jsonify({'error': 'Failed to accept friend request'}), 400

@friends_bp.route('/decline-request/<request_id>', methods=['POST'])
@jwt_required()
def decline_friend_request(request_id):
    """Decline a friend request"""
    try:
        request_uuid = uuid.UUID(request_id)
    except ValueError:
        return jsonify({'error': 'Invalid request ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    # Find friend request
    friend_request = Friend.query.get(request_uuid)
    if not friend_request:
        return jsonify({'error': 'Friend request not found'}), 404
    
    if friend_request.requestee_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Decline the request
    if Friend.reject_friend_request(request_uuid):
        db.session.commit()
        return jsonify({'message': 'Friend request declined'}), 200
    else:
        return jsonify({'error': 'Failed to decline friend request'}), 400

@friends_bp.route('/remove-friend/<user_id>', methods=['POST'])
@jwt_required()
def remove_friend(user_id):
    """Remove a friend"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    # Remove friendship
    if Friend.remove_friend(current_user_id, user_uuid):
        db.session.commit()
        return jsonify({'message': 'Friend removed successfully'}), 200
    else:
        return jsonify({'error': 'Friendship not found'}), 404

@friends_bp.route('/friends/<user_id>', methods=['GET'])
@jwt_required()
def get_friends(user_id):
    """Get friends of a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get friends
    friend_ids = Friend.get_friends(user_uuid)
    
    # Paginate manually
    start = (page - 1) * per_page
    end = start + per_page
    paginated_friend_ids = friend_ids[start:end]
    
    friends = []
    for friend_id in paginated_friend_ids:
        friend = User.query.get(friend_id)
        if friend:
            friends.append(friend.to_dict())
    
    return jsonify({
        'friends': friends,
        'total': len(friend_ids),
        'page': page,
        'per_page': per_page
    }), 200

@friends_bp.route('/pending-requests', methods=['GET'])
@jwt_required()
def get_pending_requests():
    """Get pending friend requests for current user"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get pending requests
    requests = Friend.get_pending_requests(current_user_id)
    
    # Paginate manually
    start = (page - 1) * per_page
    end = start + per_page
    paginated_requests = requests[start:end]
    
    request_data = []
    for friend_request in paginated_requests:
        requester = User.query.get(friend_request.requester_id)
        if requester:
            request_data.append({
                'request_id': str(friend_request.id),
                'requester': requester.to_dict(),
                'requested_at': friend_request.created_at.isoformat()
            })
    
    return jsonify({
        'requests': request_data,
        'total': len(requests),
        'page': page,
        'per_page': per_page
    }), 200

@friends_bp.route('/sent-requests', methods=['GET'])
@jwt_required()
def get_sent_requests():
    """Get sent friend requests by current user"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get sent requests
    requests = Friend.get_sent_requests(current_user_id)
    
    # Paginate manually
    start = (page - 1) * per_page
    end = start + per_page
    paginated_requests = requests[start:end]
    
    request_data = []
    for friend_request in paginated_requests:
        requestee = User.query.get(friend_request.requestee_id)
        if requestee:
            request_data.append({
                'request_id': str(friend_request.id),
                'requestee': requestee.to_dict(),
                'sent_at': friend_request.created_at.isoformat()
            })
    
    return jsonify({
        'requests': request_data,
        'total': len(requests),
        'page': page,
        'per_page': per_page
    }), 200

@friends_bp.route('/friends-count/<user_id>', methods=['GET'])
def get_friends_count(user_id):
    """Get friends count for a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    count = len(Friend.get_friends(user_uuid))
    return jsonify({'friends_count': count}), 200

@friends_bp.route('/are-friends/<user_id>', methods=['GET'])
@jwt_required()
def are_friends(user_id):
    """Check if current user is friends with another user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    current_user_id = get_jwt_identity()
    
    are_friends = Friend.are_friends(current_user_id, user_uuid)
    return jsonify({'are_friends': are_friends}), 200

