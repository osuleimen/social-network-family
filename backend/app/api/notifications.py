from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for current user"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=current_user_id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    notifications_data = []
    for notification in notifications.items:
        notification_dict = notification.to_dict()
        
        # Add additional user information if available
        if notification.data and 'follower_id' in notification.data:
            user = User.query.get(notification.data['follower_id'])
            if user:
                notification_dict['follower'] = user.to_dict()
        
        if notification.data and 'requester_id' in notification.data:
            user = User.query.get(notification.data['requester_id'])
            if user:
                notification_dict['requester'] = user.to_dict()
        
        if notification.data and 'accepter_id' in notification.data:
            user = User.query.get(notification.data['accepter_id'])
            if user:
                notification_dict['accepter'] = user.to_dict()
        
        notifications_data.append(notification_dict)
    
    return jsonify({
        'notifications': notifications_data,
        'total': notifications.total,
        'pages': notifications.pages,
        'current_page': page
    }), 200

@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get unread notifications count for current user"""
    current_user_id = get_jwt_identity()
    
    count = Notification.query.filter_by(
        user_id=current_user_id,
        is_read=False
    ).count()
    
    return jsonify({'unread_count': count}), 200

@notifications_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user_id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    current_user_id = get_jwt_identity()
    
    Notification.query.filter_by(
        user_id=current_user_id,
        is_read=False
    ).update({'is_read': True})
    
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200

@notifications_bp.route('/delete/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user_id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification deleted successfully'}), 200

@notifications_bp.route('/delete-all', methods=['DELETE'])
@jwt_required()
def delete_all_notifications():
    """Delete all notifications for current user"""
    current_user_id = get_jwt_identity()
    
    Notification.query.filter_by(user_id=current_user_id).delete()
    db.session.commit()
    
    return jsonify({'message': 'All notifications deleted successfully'}), 200

@notifications_bp.route('/types', methods=['GET'])
def get_notification_types():
    """Get available notification types"""
    types = [
        {
            'type': 'like',
            'title': 'Like',
            'description': 'Someone liked your post'
        },
        {
            'type': 'comment',
            'title': 'Comment',
            'description': 'Someone commented on your post'
        },
        {
            'type': 'follow',
            'title': 'Follow',
            'description': 'Someone started following you'
        },
        {
            'type': 'friend_request',
            'title': 'Friend Request',
            'description': 'Someone sent you a friend request'
        },
        {
            'type': 'friend_accepted',
            'title': 'Friend Accepted',
            'description': 'Someone accepted your friend request'
        },
        {
            'type': 'mention',
            'title': 'Mention',
            'description': 'Someone mentioned you in a post'
        }
    ]
    
    return jsonify({'notification_types': types}), 200



