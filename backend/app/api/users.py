from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Follow, Notification
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import or_

users_bp = Blueprint('users', __name__)

class UpdateUserSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    bio = fields.Str()
    avatar_url = fields.Str()
    gramps_person_id = fields.Str()
    gramps_tree_id = fields.Str()

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = User.query.filter(User.is_active == True)
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get users'}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user by ID"""
    try:
        user = User.query.get_or_404(user_id)
        
        if not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if current user is following this user
        is_following = False
        if current_user and current_user.id != user.id:
            is_following = current_user.following.filter_by(followed_id=user.id).first() is not None
        
        user_data = user.to_dict()
        user_data['is_following'] = is_following
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user'}), 500

@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        schema = UpdateUserSchema()
        data = schema.load(request.json)
        
        for key, value in data.items():
            setattr(user, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@users_bp.route('/<int:user_id>/follow', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    """Follow a user"""
    try:
        current_user_id = get_jwt_identity()
        
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot follow yourself'}), 400
        
        user_to_follow = User.query.get_or_404(user_id)
        
        if not user_to_follow.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already following
        existing_follow = Follow.query.filter_by(
            follower_id=current_user_id,
            followed_id=user_id
        ).first()
        
        if existing_follow:
            return jsonify({'error': 'Already following this user'}), 400
        
        # Create follow relationship
        follow = Follow(follower_id=current_user_id, followed_id=user_id)
        db.session.add(follow)
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            type='follow',
            title='New Follower',
            message=f'Someone started following you',
            data={'follower_id': current_user_id}
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({'message': 'Successfully followed user'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to follow user'}), 500

@users_bp.route('/<int:user_id>/unfollow', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    """Unfollow a user"""
    try:
        current_user_id = get_jwt_identity()
        
        follow = Follow.query.filter_by(
            follower_id=current_user_id,
            followed_id=user_id
        ).first()
        
        if not follow:
            return jsonify({'error': 'Not following this user'}), 400
        
        db.session.delete(follow)
        db.session.commit()
        
        return jsonify({'message': 'Successfully unfollowed user'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to unfollow user'}), 500

@users_bp.route('/<int:user_id>/followers', methods=['GET'])
@jwt_required()
def get_followers(user_id):
    """Get user's followers"""
    try:
        user = User.query.get_or_404(user_id)
        
        if not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        followers = user.followers.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'followers': [follow.follower.to_dict() for follow in followers.items],
            'total': followers.total,
            'pages': followers.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get followers'}), 500

@users_bp.route('/<int:user_id>/following', methods=['GET'])
@jwt_required()
def get_following(user_id):
    """Get users that this user is following"""
    try:
        user = User.query.get_or_404(user_id)
        
        if not user.is_active:
            return jsonify({'error': 'User not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        following = user.following.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'following': [follow.followed.to_dict() for follow in following.items],
            'total': following.total,
            'pages': following.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get following'}), 500
