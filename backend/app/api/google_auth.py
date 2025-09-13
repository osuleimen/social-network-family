from flask import Blueprint, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User
from app.services.google_oauth_service import google_oauth_service
from app.services.error_handler import auth_error_handler
from app import db
import logging
import secrets

logger = logging.getLogger(__name__)

google_auth_bp = Blueprint('google_auth', __name__)

@google_auth_bp.route('/login', methods=['GET'])
def google_login():
    """Initiate Google OAuth login"""
    try:
        if not google_oauth_service.is_configured():
            return jsonify({'error': 'Google OAuth not configured'}), 500
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Get authorization URL
        auth_url = google_oauth_service.get_auth_url(state)
        
        return jsonify({
            'auth_url': auth_url,
            'state': state
        }), 200
        
    except Exception as e:
        logger.error(f"Error in google_login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@google_auth_bp.route('/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            logger.error(f"Google OAuth error: {error}")
            return redirect(f"https://my.ozimiz.org/auth?error=oauth_error&message={error}")
        
        if not code:
            return redirect(f"https://my.ozimiz.org/auth?error=no_code&message=Authorization code not provided")
        
        # Exchange code for token
        token_result = google_oauth_service.exchange_code_for_token(code)
        
        if not token_result['success']:
            logger.error(f"Token exchange failed: {token_result.get('error')}")
            return redirect(f"https://my.ozimiz.org/auth?error=token_exchange&message={token_result.get('error')}")
        
        # Get user info
        user_info_result = google_oauth_service.get_user_info(token_result['access_token'])
        
        if not user_info_result['success']:
            logger.error(f"Failed to get user info: {user_info_result.get('error')}")
            return redirect(f"https://my.ozimiz.org/auth?error=user_info&message={user_info_result.get('error')}")
        
        user_data = user_info_result['user_data']
        
        # Find or create user
        user = User.find_by_google_id(user_data['google_id'])
        
        if not user:
            # Check if user exists with same email
            user = User.find_by_email(user_data['email'])
            
            if user:
                # Update existing user with Google info
                user.google_id = user_data['google_id']
                user.google_picture = user_data['picture']
                user.auth_method = 'google'
                if not user.first_name:
                    user.first_name = user_data['first_name']
                if not user.last_name:
                    user.last_name = user_data['last_name']
                if not user.avatar_url:
                    user.avatar_url = user_data['picture']
                db.session.commit()
                
                logger.info(f"Updated existing user {user.id} with Google info")
                is_new_user = False
            else:
                # Create new user
                user = User.create_from_google(user_data)
                db.session.add(user)
                db.session.commit()
                
                logger.info(f"Created new user for Google ID {user_data['google_id']}")
                is_new_user = True
        else:
            logger.info(f"User {user.id} authenticated via Google")
            is_new_user = False
        
        # Generate JWT tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Redirect to frontend with tokens in query parameters
        frontend_url = f"https://my.ozimiz.org/auth?success=true&access_token={access_token}&refresh_token={refresh_token}&is_new_user={is_new_user}&auth_method=google"
        
        return redirect(frontend_url)
        
    except Exception as e:
        logger.error(f"Error in google_callback: {str(e)}")
        return redirect(f"https://my.ozimiz.org/auth?error=internal_error&message=Internal server error")

@google_auth_bp.route('/success', methods=['GET'])
def google_success():
    """Handle successful Google authentication (for API calls)"""
    try:
        access_token = request.args.get('access_token')
        refresh_token = request.args.get('refresh_token')
        is_new_user = request.args.get('is_new_user', 'false').lower() == 'true'
        
        if not access_token or not refresh_token:
            return jsonify({'error': 'Authentication tokens not provided'}), 400
        
        # This endpoint is mainly for API testing
        # In production, the callback should redirect to frontend
        return jsonify({
            'message': 'Google authentication successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'is_new_user': is_new_user
        }), 200
        
    except Exception as e:
        logger.error(f"Error in google_success: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
