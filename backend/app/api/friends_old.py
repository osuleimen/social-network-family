from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.friend import Friend, FriendStatus
from app.models.notification import Notification
from datetime import datetime
import uuid

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/send-request/<int:user_id>', methods=['POST'])
@jwt_required()
def send_friend_request(user_id):
    """Send a friend request"""
    current_user_id = get_jwt_identity()
    
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot send friend request to yourself'}), 400
    
    # Check if user exists
    user_to_friend = User.query.get(user_id)
    if not user_to_friend:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if already friends or request exists
    existing_friendship = Friend.query.filter(
        ((Friend.user1_id == current_user_id) & (Friend.user2_id == user_id)) |
        ((Friend.user1_id == user_id) & (Friend.user2_id == current_user_id))
    ).first()
    
    if existing_friendship:
        if existing_friendship.status == 'accepted':
            return jsonify({'error': 'Already friends'}), 400
        elif existing_friendship.status == 'pending':
            return jsonify({'error': 'Friend request already sent'}), 400
        elif existing_friendship.status == 'blocked':
            return jsonify({'error': 'Cannot send friend request'}), 400
    
    # Create friend request
    friend_request = Friend(
        user1_id=current_user_id,
        user2_id=user_id,
        status='pending'
    )
    db.session.add(friend_request)
    
    # Create notification
    current_user = User.query.get(current_user_id)
    notification = Notification(
        user_id=user_id,
        type='friend_request',
        title='Friend Request',
        message=f'{current_user.first_name or current_user.username or "Someone"} sent you a friend request',
        data={'requester_id': current_user_id, 'requester_name': current_user.first_name or current_user.username}
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Friend request sent successfully',
        'friend_request': friend_request.to_dict()
    }), 201

@friends_bp.route('/accept-request/<int:request_id>', methods=['POST'])
@jwt_required()
def accept_friend_request(request_id):
    """Accept a friend request"""
    current_user_id = get_jwt_identity()
    
    # Find friend request
    friend_request = Friend.query.get(request_id)
    if not friend_request:
        return jsonify({'error': 'Friend request not found'}), 404
    
    if friend_request.user2_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if friend_request.status != 'pending':
        return jsonify({'error': 'Friend request is not pending'}), 400
    
    # Accept the request
    friend_request.status = 'accepted'
    friend_request.updated_at = datetime.utcnow()
    
    # Create notification for the requester
    current_user = User.query.get(current_user_id)
    notification = Notification(
        user_id=friend_request.user1_id,
        type='friend_accepted',
        title='Friend Request Accepted',
        message=f'{current_user.first_name or current_user.username or "Someone"} accepted your friend request',
        data={'accepter_id': current_user_id, 'accepter_name': current_user.first_name or current_user.username}
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Friend request accepted successfully',
        'friendship': friend_request.to_dict()
    }), 200

@friends_bp.route('/decline-request/<int:request_id>', methods=['POST'])
@jwt_required()
def decline_friend_request(request_id):
    """Decline a friend request"""
    current_user_id = get_jwt_identity()
    
    # Find friend request
    friend_request = Friend.query.get(request_id)
    if not friend_request:
        return jsonify({'error': 'Friend request not found'}), 404
    
    if friend_request.user2_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if friend_request.status != 'pending':
        return jsonify({'error': 'Friend request is not pending'}), 400
    
    # Decline the request
    friend_request.status = 'declined'
    friend_request.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Friend request declined successfully'}), 200

@friends_bp.route('/remove-friend/<int:user_id>', methods=['POST'])
@jwt_required()
def remove_friend(user_id):
    """Remove a friend"""
    current_user_id = get_jwt_identity()
    
    # Find friendship
    friendship = Friend.query.filter(
        ((Friend.user1_id == current_user_id) & (Friend.user2_id == user_id)) |
        ((Friend.user1_id == user_id) & (Friend.user2_id == current_user_id))
    ).filter_by(status='accepted').first()
    
    if not friendship:
        return jsonify({'error': 'Friendship not found'}), 404
    
    db.session.delete(friendship)
    db.session.commit()
    
    return jsonify({'message': 'Friend removed successfully'}), 200

@friends_bp.route('/block-user/<int:user_id>', methods=['POST'])
@jwt_required()
def block_user(user_id):
    """Block a user"""
    current_user_id = get_jwt_identity()
    
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot block yourself'}), 400
    
    # Find existing relationship
    relationship = Friend.query.filter(
        ((Friend.user1_id == current_user_id) & (Friend.user2_id == user_id)) |
        ((Friend.user1_id == user_id) & (Friend.user2_id == current_user_id))
    ).first()
    
    if relationship:
        relationship.status = 'blocked'
        relationship.updated_at = datetime.utcnow()
    else:
        relationship = Friend(
            user1_id=current_user_id,
            user2_id=user_id,
            status='blocked'
        )
        db.session.add(relationship)
    
    db.session.commit()
    
    return jsonify({'message': 'User blocked successfully'}), 200

@friends_bp.route('/unblock-user/<int:user_id>', methods=['POST'])
@jwt_required()
def unblock_user(user_id):
    """Unblock a user"""
    current_user_id = get_jwt_identity()
    
    # Find blocked relationship
    relationship = Friend.query.filter(
        ((Friend.user1_id == current_user_id) & (Friend.user2_id == user_id)) |
        ((Friend.user1_id == user_id) & (Friend.user2_id == current_user_id))
    ).filter_by(status='blocked').first()
    
    if not relationship:
        return jsonify({'error': 'User is not blocked'}), 404
    
    db.session.delete(relationship)
    db.session.commit()
    
    return jsonify({'message': 'User unblocked successfully'}), 200

@friends_bp.route('/friends/<int:user_id>', methods=['GET'])
@jwt_required()
def get_friends(user_id):
    """Get friends of a user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    friends = Friend.query.filter(
        ((Friend.user1_id == user_id) | (Friend.user2_id == user_id))
    ).filter_by(status='accepted').paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    friend_users = []
    for friendship in friends.items:
        friend_id = friendship.user2_id if friendship.user1_id == user_id else friendship.user1_id
        user = User.query.get(friend_id)
        if user:
            friend_users.append({
                'user': user.to_dict(),
                'friends_since': friendship.created_at.isoformat()
            })
    
    return jsonify({
        'friends': friend_users,
        'total': friends.total,
        'pages': friends.pages,
        'current_page': page
    }), 200

@friends_bp.route('/pending-requests', methods=['GET'])
@jwt_required()
def get_pending_requests():
    """Get pending friend requests for current user"""
    current_user_id = get_jwt_identity()
    
    pending_requests = Friend.get_pending_requests(current_user_id)
    
    requests_data = []
    for request in pending_requests:
        requester = User.query.get(request.user1_id)
        if requester:
            requests_data.append({
                'request': request.to_dict(),
                'requester': requester.to_dict()
            })
    
    return jsonify({'pending_requests': requests_data}), 200

@friends_bp.route('/sent-requests', methods=['GET'])
@jwt_required()
def get_sent_requests():
    """Get sent friend requests by current user"""
    current_user_id = get_jwt_identity()
    
    sent_requests = Friend.get_sent_requests(current_user_id)
    
    requests_data = []
    for request in sent_requests:
        recipient = User.query.get(request.user2_id)
        if recipient:
            requests_data.append({
                'request': request.to_dict(),
                'recipient': recipient.to_dict()
            })
    
    return jsonify({'sent_requests': requests_data}), 200

@friends_bp.route('/friends-count/<int:user_id>', methods=['GET'])
def get_friends_count(user_id):
    """Get friends count for a user"""
    count = Friend.query.filter(
        ((Friend.user1_id == user_id) | (Friend.user2_id == user_id))
    ).filter_by(status='accepted').count()
    return jsonify({'friends_count': count}), 200


