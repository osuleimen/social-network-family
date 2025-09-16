from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserRole, UserStatus
from app.models.post import Post
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.report import Report, ReportStatus
from datetime import datetime, timedelta
from sqlalchemy import or_, func
import uuid

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Decorator to require admin role"""
    def decorator(f):
        def admin_decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.can_admin():
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        admin_decorated_function.__name__ = f.__name__
        return admin_decorated_function
    return decorator

def require_moderator():
    """Decorator to require moderator or admin role"""
    def decorator(f):
        def moderator_decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.can_moderate():
                return jsonify({'error': 'Moderator access required'}), 403
            
            return f(*args, **kwargs)
        moderator_decorated_function.__name__ = f.__name__
        return moderator_decorated_function
    return decorator

def require_superadmin():
    """Decorator to require superadmin role"""
    def decorator(f):
        def superadmin_decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.is_superadmin():
                return jsonify({'error': 'SuperAdmin access required'}), 403
            
            return f(*args, **kwargs)
        superadmin_decorated_function.__name__ = f.__name__
        return superadmin_decorated_function
    return decorator

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin()
def get_all_users():
    """Get all users with pagination and search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    
    query = User.query
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search),
                User.display_name.contains(search)
            )
        )
    
    if role:
        try:
            query = query.filter(User.role == UserRole(role))
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
    
    if status:
        try:
            query = query.filter(User.status == UserStatus(status))
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users_data = []
    for user in users.items:
        user_dict = user.to_dict(include_pii=True)  # Admin can see PII
        # Add additional admin info
        user_dict['posts_count'] = Post.query.filter_by(author_id=user.id).count()
        user_dict['followers_count'] = user.followers.count() if hasattr(user, 'followers') else 0
        user_dict['following_count'] = user.following.count() if hasattr(user, 'following') else 0
        users_data.append(user_dict)
    
    return jsonify({
        'users': users_data,
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200

@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
@require_admin()
def get_user_details(user_id):
    """Get detailed information about a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_dict = user.to_dict(include_pii=True)  # Admin can see PII
    
    # Add detailed statistics
    user_dict['posts_count'] = Post.query.filter_by(author_id=user.id).count()
    user_dict['comments_count'] = Comment.query.filter_by(author_id=user.id).count()
    user_dict['followers_count'] = user.followers.count() if hasattr(user, 'followers') else 0
    user_dict['following_count'] = user.following.count() if hasattr(user, 'following') else 0
    
    # Recent activity
    recent_posts = Post.query.filter_by(author_id=user.id).order_by(Post.created_at.desc()).limit(5).all()
    user_dict['recent_posts'] = [post.to_dict() for post in recent_posts]
    
    return jsonify({'user': user_dict}), 200

@admin_bp.route('/users/<user_id>/ban', methods=['POST'])
@jwt_required()
@require_admin()
def ban_user(user_id):
    """Ban a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    ban_reason = data.get('reason', '')
    ban_duration = data.get('duration_days', None)  # None for permanent ban
    
    user.status = UserStatus.BLOCKED
    user.ban_reason = ban_reason
    
    if ban_duration:
        user.banned_until = datetime.utcnow() + timedelta(days=ban_duration)
    else:
        user.banned_until = None  # Permanent ban
    
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="ban_user",
        target_type="user",
        target_id=user.id,
        action_metadata={
            "reason": ban_reason,
            "duration_days": ban_duration,
            "permanent": ban_duration is None
        }
    )
    db.session.commit()
    
    return jsonify({'message': 'User banned successfully'}), 200

@admin_bp.route('/users/<user_id>/unban', methods=['POST'])
@jwt_required()
@require_admin()
def unban_user(user_id):
    """Unban a user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.status = UserStatus.ACTIVE
    user.ban_reason = None
    user.banned_until = None
    
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="unban_user",
        target_type="user",
        target_id=user.id,
        action_metadata={}
    )
    db.session.commit()
    
    return jsonify({'message': 'User unbanned successfully'}), 200

@admin_bp.route('/users/<user_id>/role', methods=['PUT'])
@jwt_required()
@require_superadmin()  # Only SuperAdmin can change roles
def update_user_role(user_id):
    """Update user role"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in [role.value for role in UserRole]:
        return jsonify({'error': 'Invalid role'}), 400
    
    old_role = user.role.value
    user.role = UserRole(new_role)
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="change_user_role",
        target_type="user",
        target_id=user.id,
        action_metadata={
            "old_role": old_role,
            "new_role": new_role
        }
    )
    db.session.commit()
    
    return jsonify({'message': 'User role updated successfully'}), 200

@admin_bp.route('/posts', methods=['GET'])
@jwt_required()
@require_moderator()
def get_all_posts():
    """Get all posts with pagination and filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    author_id = request.args.get('author_id')
    
    query = Post.query.filter_by(is_deleted=False)
    
    if search:
        query = query.filter(Post.caption.contains(search))
    
    if author_id:
        try:
            author_uuid = uuid.UUID(author_id)
            query = query.filter(Post.author_id == author_uuid)
        except ValueError:
            return jsonify({'error': 'Invalid author ID format'}), 400
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts_data = []
    for post in posts.items:
        post_dict = post.to_dict()
        posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    }), 200

@admin_bp.route('/posts/<post_id>/delete', methods=['DELETE'])
@jwt_required()
@require_moderator()
def delete_post(post_id):
    """Delete a post (soft delete)"""
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        return jsonify({'error': 'Invalid post ID format'}), 400
    
    post = Post.query.get(post_uuid)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    post.is_deleted = True
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="delete_post",
        target_type="post",
        target_id=post.id,
        action_metadata={
            "author_id": str(post.author_id),
            "caption": post.caption[:100] + "..." if len(post.caption) > 100 else post.caption
        }
    )
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

@admin_bp.route('/comments/<comment_id>/delete', methods=['DELETE'])
@jwt_required()
@require_moderator()
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        comment_uuid = uuid.UUID(comment_id)
    except ValueError:
        return jsonify({'error': 'Invalid comment ID format'}), 400
    
    comment = Comment.query.get(comment_uuid)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    db.session.delete(comment)
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="delete_comment",
        target_type="comment",
        target_id=comment.id,
        action_metadata={
            "author_id": str(comment.author_id),
            "post_id": str(comment.post_id),
            "text": comment.text[:100] + "..." if len(comment.text) > 100 else comment.text
        }
    )
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_admin()
def get_admin_stats():
    """Get admin statistics"""
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(status=UserStatus.ACTIVE).count(),
        'blocked_users': User.query.filter_by(status=UserStatus.BLOCKED).count(),
        'total_posts': Post.query.filter_by(is_deleted=False).count(),
        'total_comments': Comment.query.count(),
        'total_notifications': Notification.query.count(),
        'unread_notifications': Notification.query.filter_by(read=False).count(),
        'users_by_role': {
            'superadmin': User.query.filter_by(role=UserRole.SUPERADMIN).count(),
            'admin': User.query.filter_by(role=UserRole.ADMIN).count(),
            'moderator': User.query.filter_by(role=UserRole.MODERATOR).count(),
            'user': User.query.filter_by(role=UserRole.USER).count()
        },
        'reports': {
            'pending': Report.query.filter_by(status=ReportStatus.PENDING).count(),
            'reviewed': Report.query.filter_by(status=ReportStatus.REVIEWED).count(),
            'resolved': Report.query.filter_by(status=ReportStatus.RESOLVED).count(),
            'rejected': Report.query.filter_by(status=ReportStatus.REJECTED).count()
        }
    }
    
    return jsonify({'stats': stats}), 200

@admin_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
@require_admin()
def get_recent_activity():
    """Get recent activity for admin dashboard"""
    recent_posts = Post.query.filter_by(is_deleted=False).order_by(Post.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_notifications = Notification.query.order_by(Notification.created_at.desc()).limit(10).all()
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(10).all()
    
    return jsonify({
        'recent_posts': [post.to_dict() for post in recent_posts],
        'recent_users': [user.to_dict(include_pii=True) for user in recent_users],
        'recent_notifications': [notification.to_dict() for notification in recent_notifications],
        'recent_reports': [report.to_dict() for report in recent_reports]
    }), 200

@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@require_admin()
def get_audit_logs():
    """Get audit logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    action = request.args.get('action', '')
    actor_id = request.args.get('actor_id', '')
    
    query = AuditLog.query
    
    if action:
        query = query.filter(AuditLog.action.contains(action))
    
    if actor_id:
        try:
            actor_uuid = uuid.UUID(actor_id)
            query = query.filter(AuditLog.actor_id == actor_uuid)
        except ValueError:
            return jsonify({'error': 'Invalid actor ID format'}), 400
    
    logs = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    }), 200

@admin_bp.route('/impersonate/<user_id>', methods=['POST'])
@jwt_required()
@require_superadmin()  # Only SuperAdmin can impersonate
def impersonate_user(user_id):
    """Impersonate a user (SuperAdmin only with 2FA)"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # TODO: Implement 2FA verification here
    # For now, just log the impersonation attempt
    
    # Log the action
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="impersonate_user",
        target_type="user",
        target_id=user.id,
        action_metadata={
            "impersonated_user": str(user.id),
            "impersonated_username": user.username
        }
    )
    db.session.commit()
    
    # TODO: Generate temporary token for impersonation
    # For now, just return success
    return jsonify({
        'message': 'Impersonation logged successfully',
        'impersonated_user': user.to_dict()
    }), 200

@admin_bp.route('/export-user-data/<user_id>', methods=['GET'])
@jwt_required()
@require_admin()
def export_user_data(user_id):
    """Export user data for GDPR compliance"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Collect all user data
    user_data = {
        'user': user.to_dict(include_pii=True),
        'posts': [post.to_dict() for post in Post.query.filter_by(author_id=user.id).all()],
        'comments': [comment.to_dict() for comment in Comment.query.filter_by(author_id=user.id).all()],
        'notifications': [notification.to_dict() for notification in Notification.query.filter_by(user_id=user.id).all()],
        'audit_logs': [log.to_dict() for log in AuditLog.query.filter_by(actor_id=user.id).all()]
    }
    
    # Log the export
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="export_user_data",
        target_type="user",
        target_id=user.id,
        action_metadata={
            "exported_by": "admin",
            "data_types": list(user_data.keys())
        }
    )
    db.session.commit()
    
    return jsonify(user_data), 200

@admin_bp.route('/delete-user-data/<user_id>', methods=['DELETE'])
@jwt_required()
@require_superadmin()  # Only SuperAdmin can delete user data
def delete_user_data(user_id):
    """Delete user data for GDPR compliance"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    user = User.query.get(user_uuid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Log the deletion before doing it
    AuditLog.log_action(
        actor_id=get_jwt_identity(),
        action="delete_user_data",
        target_type="user",
        target_id=user.id,
        action_metadata={
            "deleted_by": "superadmin",
            "user_email": user.email,
            "user_username": user.username
        }
    )
    
    # TODO: Implement proper data deletion
    # For now, just deactivate the user
    user.status = UserStatus.DEACTIVATED
    db.session.commit()
    
    return jsonify({'message': 'User data deletion initiated'}), 200
