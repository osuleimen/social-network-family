from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, UserRole, AuditLog
from app import db
from datetime import datetime
import uuid

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict(include_pii=True)), 200

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    
    # Update basic fields
    if 'display_name' in data:
        user.display_name = data['display_name']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': 'Email already taken'}), 400
        user.email = data['email']
    if 'bio' in data:
        user.bio = data['bio']
    if 'website' in data:
        user.website = data['website']
    if 'location' in data:
        user.location = data['location']
    if 'pronouns' in data:
        user.pronouns = data['pronouns']
    if 'private_account' in data:
        user.private_account = data['private_account']
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    if 'gramps_person_id' in data:
        user.gramps_person_id = data['gramps_person_id']
    if 'gramps_tree_id' in data:
        user.gramps_tree_id = data['gramps_tree_id']
    
    # Log the profile update
    AuditLog.log_action(
        actor_id=current_user_id,
        action="update_profile",
        target_type="user",
        target_id=current_user_id,
        action_metadata={"updated_fields": list(data.keys())}
    )
    
    db.session.commit()
    return jsonify({'user': user.to_dict(include_pii=True), 'message': 'Profile updated successfully'}), 200

@users_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    # Verify current password
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Set new password
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200

@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user = User.query.get_or_404(user_uuid)
    
    return jsonify(user.to_dict(requesting_user=current_user)), 200

@users_bp.route('/by-username/<username>', methods=['GET'])
@jwt_required()
def get_user_by_username(username):
    """Get user by username"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user = User.find_by_username(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict(requesting_user=current_user)), 200

@users_bp.route('/by-slug/<profile_slug>', methods=['GET'])
@jwt_required()
def get_user_by_slug(profile_slug):
    """Get user by profile slug"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user = User.find_by_slug_or_previous(profile_slug)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # If user was found by previous slug, return redirect info
    response_data = user.to_dict(requesting_user=current_user)
    if user.profile_slug != profile_slug:
        response_data['redirect_to'] = user.get_public_profile_url()
    
    return jsonify(response_data), 200

@users_bp.route('/profile/username', methods=['PUT'])
@jwt_required()
def update_username():
    """Update username and profile slug"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    new_username = data.get('username', '').strip()
    
    if not new_username:
        return jsonify({'error': 'Username is required'}), 400
    
    if len(new_username) > 30:
        return jsonify({'error': 'Username must be 30 characters or less'}), 400
    
    # Check for forbidden words
    forbidden_words = ['admin', 'api', 'www', 'root', 'system', 'support']
    if new_username.lower() in forbidden_words:
        return jsonify({'error': 'Username is not allowed'}), 400
    
    # Update username and slug
    if user.update_username_and_slug(new_username):
        # Log the username change
        AuditLog.log_action(
            actor_id=current_user_id,
            action="change_username",
            target_type="user",
            target_id=current_user_id,
            action_metadata={
                "old_username": user.username,
                "new_username": new_username,
                "old_slug": user.profile_slug
            }
        )
        
        db.session.commit()
        return jsonify({
            'user': user.to_dict(include_pii=True),
            'message': 'Username updated successfully'
        }), 200
    else:
        return jsonify({'error': 'Username is already taken'}), 400

@users_bp.route('/profile/avatar', methods=['PUT'])
@jwt_required()
def update_avatar():
    """Update user avatar"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    avatar_media_id = data.get('avatar_media_id')
    
    if avatar_media_id:
        try:
            # Validate that the media belongs to the user
            from app.models import Media
            media = Media.query.get(uuid.UUID(avatar_media_id))
            if not media or media.owner_id != user.id:
                return jsonify({'error': 'Invalid media ID'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid media ID format'}), 400
    
    user.avatar_media_id = avatar_media_id
    
    # Log the avatar change
    AuditLog.log_action(
        actor_id=current_user_id,
        action="change_avatar",
        target_type="user",
        target_id=current_user_id,
        action_metadata={"avatar_media_id": avatar_media_id}
    )
    
    db.session.commit()
    return jsonify({
        'user': user.to_dict(include_pii=True),
        'message': 'Avatar updated successfully'
    }), 200

@users_bp.route('/profile/privacy', methods=['PUT'])
@jwt_required()
def update_privacy():
    """Update privacy settings"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    
    if 'private_account' in data:
        user.private_account = data['private_account']
    
    # Log the privacy change
    AuditLog.log_action(
        actor_id=current_user_id,
        action="update_privacy",
        target_type="user",
        target_id=current_user_id,
        action_metadata={"private_account": user.private_account}
    )
    
    db.session.commit()
    return jsonify({
        'user': user.to_dict(include_pii=True),
        'message': 'Privacy settings updated successfully'
    }), 200
