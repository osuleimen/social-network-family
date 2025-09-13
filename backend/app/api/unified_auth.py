from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.code import Code
from app.services.sms_service import sms_service
from app.services.email_service import email_service
from app.services.rate_limiter import rate_limiter
import logging
import re

logger = logging.getLogger(__name__)

unified_auth_bp = Blueprint('unified_auth', __name__)

def detect_identifier_type(identifier: str) -> str:
    """Detect if identifier is phone or email"""
    # Remove all non-digit characters for phone detection
    digits_only = re.sub(r'\D', '', identifier)
    
    # Email detection
    if '@' in identifier and '.' in identifier:
        return 'email'
    
    # Phone detection (8-11 digits)
    if 8 <= len(digits_only) <= 11:
        return 'phone'
    
    # Default to phone for now
    return 'phone'

def format_phone_number(phone: str) -> str:
    """Format phone number to international format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle different formats
    if digits.startswith('8') and len(digits) == 11:
        # Russian format: 8XXXXXXXXXX -> +7XXXXXXXXX
        digits = '7' + digits[1:]
    elif digits.startswith('7') and len(digits) == 11:
        # Already in correct format
        pass
    elif len(digits) == 10:
        # Add country code
        digits = '7' + digits
    
    return '+' + digits

@unified_auth_bp.route('/request-code', methods=['POST'])
def request_code():
    """Request verification code for phone or email"""
    try:
        data = request.get_json()
        logger.info(f"Request data: {data}")
        identifier = data.get('identifier', '').strip()
        logger.info(f"Extracted identifier: '{identifier}'")
        
        if not identifier:
            logger.warning(f"Empty identifier received. Data: {data}")
            return jsonify({'error': 'Identifier is required'}), 400
        
        # Detect type and format
        identifier_type = detect_identifier_type(identifier)
        
        if identifier_type == 'phone':
            formatted_identifier = format_phone_number(identifier)
        else:
            formatted_identifier = identifier.lower()
        
        # Check rate limiting (3 requests per minute)
        if not rate_limiter.is_allowed(formatted_identifier, max_requests=3, window_minutes=1):
            remaining_time = rate_limiter.get_remaining_time(formatted_identifier)
            return jsonify({
                'error': f'Слишком много запросов. Подождите {remaining_time} секунд перед повторной отправкой'
            }), 429
        
        # Check if user exists
        user = User.find_by_identifier(formatted_identifier)
        is_new_user = user is None
        
        # If user is registered, don't send code automatically
        if not is_new_user:
            logger.info(f"Registered user {formatted_identifier} - not sending code automatically")
            return jsonify({
                'success': True,
                'identifier': formatted_identifier,
                'type': identifier_type,
                'is_new_user': False,
                'has_existing_code': False,
                'message': 'Пользователь уже зарегистрирован. Введите код, отправленный ранее, или запросите новый код.',
                'requires_manual_code_request': True
            }), 200
        
        # Create or find active code for new users
        existing_code = Code.find_active_code_for_identifier(formatted_identifier)
        
        if existing_code and not existing_code.is_expired():
            # Return existing code info for new users
            logger.info(f"Existing code for new user {formatted_identifier}: [HASHED]")
            return jsonify({
                'success': True,
                'identifier': formatted_identifier,
                'type': identifier_type,
                'is_new_user': True,
                'has_existing_code': True,
                'message': 'Code already exists and is still valid'
            }), 200
        
        # Generate new code
        verification_code, plain_code = Code.create_code(formatted_identifier, identifier_type, user.id if user else None)
        db.session.add(verification_code)
        db.session.commit()
        
        # Send code
        if identifier_type == 'phone':
            # SMS sending
            # Always send through Mobizon API
            logger.info(f"Attempting to send SMS to {formatted_identifier} with code {plain_code}")
            success = sms_service.send_verification_code(formatted_identifier, plain_code)
            logger.info(f"SMS sending result: {success}")
            # Also log for test number
            if formatted_identifier == '+77019990438':  # Test number
                logger.info(f"TEST SMS CODE for {formatted_identifier}: {plain_code}")
        else:
            # Email sending
            success = email_service.send_verification_code(formatted_identifier, plain_code)
        
        if not success:
            # If sending failed, remove the code
            db.session.delete(verification_code)
            db.session.commit()
            return jsonify({'error': f'Failed to send {identifier_type} verification code'}), 500
        
        logger.info(f"Code sent successfully to {formatted_identifier}")
        
        return jsonify({
            'success': True,
            'identifier': formatted_identifier,
            'type': identifier_type,
            'is_new_user': is_new_user,
            'has_existing_code': False,
            'message': f'Verification code sent to {identifier_type}'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in request_code: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    """Verify code and authenticate user"""
    try:
        data = request.get_json()
        identifier = data.get('identifier', '').strip()
        code = data.get('code', '').strip()
        
        if not identifier or not code:
            return jsonify({'error': 'Identifier and code are required'}), 400
        
        if len(code) != 6 or not code.isdigit():
            return jsonify({'error': 'Code must be 6 digits'}), 400
        
        # Detect type and format
        identifier_type = detect_identifier_type(identifier)
        
        if identifier_type == 'phone':
            formatted_identifier = format_phone_number(identifier)
        else:
            formatted_identifier = identifier.lower()
        
        # Find and verify code
        verification = Code.find_active_code(formatted_identifier, code)
        
        if not verification:
            return jsonify({'error': 'Invalid or expired verification code'}), 400
        
        if not verification.verify(code):
            return jsonify({'error': 'Invalid verification code'}), 400
        
        # Find or create user
        user = User.find_by_identifier(formatted_identifier)
        
        if not user:
            # Create new user
            user = User.create_from_identifier(
                identifier=formatted_identifier,
                user_type=identifier_type,
                first_name='Пользователь',  # Default name
                last_name='',
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Created new user for {formatted_identifier}")
            is_new_user = True
        else:
            logger.info(f"User {user.id} authenticated via {identifier_type}")
            is_new_user = False
        
        # Generate JWT tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Mark code as verified and deactivate
        verification.verified_at = db.func.now()
        verification.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'is_new_user': is_new_user
        }), 200
        
    except Exception as e:
        logger.error(f"Error in verify_code: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_auth_bp.route('/resend-code', methods=['POST'])
def resend_code():
    """Resend verification code"""
    try:
        data = request.get_json()
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({'error': 'Identifier is required'}), 400
        
        # Detect type and format
        identifier_type = detect_identifier_type(identifier)
        
        if identifier_type == 'phone':
            formatted_identifier = format_phone_number(identifier)
        else:
            formatted_identifier = identifier.lower()
        
        # Deactivate existing codes
        Code.query.filter_by(identifier=formatted_identifier, is_active=True).update({'is_active': False})
        db.session.commit()
        
        # Create new code
        user = User.find_by_identifier(formatted_identifier)
        verification_code, plain_code = Code.create_code(formatted_identifier, identifier_type, user.id if user else None)
        db.session.add(verification_code)
        db.session.commit()
        
        # Send code
        if identifier_type == 'phone':
            # SMS sending
            # Always send through Mobizon API
            logger.info(f"Attempting to send SMS to {formatted_identifier} with code {plain_code}")
            success = sms_service.send_verification_code(formatted_identifier, plain_code)
            logger.info(f"SMS sending result: {success}")
            # Also log for test number
            if formatted_identifier == '+77019990438':  # Test number
                logger.info(f"TEST SMS CODE for {formatted_identifier}: {plain_code}")
        else:
            # Email sending
            success = email_service.send_verification_code(formatted_identifier, plain_code)
        
        if not success:
            # If sending failed, remove the code
            db.session.delete(verification_code)
            db.session.commit()
            return jsonify({'error': f'Failed to send {identifier_type} verification code'}), 500
        
        return jsonify({
            'success': True,
            'message': f'New verification code sent to {identifier_type}'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in resend_code: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_auth_bp.route('/force-send-code', methods=['POST'])
def force_send_code():
    """Force send verification code (for registered users)"""
    try:
        data = request.get_json()
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({'error': 'Identifier is required'}), 400
        
        # Detect type and format
        identifier_type = detect_identifier_type(identifier)
        
        if identifier_type == 'phone':
            formatted_identifier = format_phone_number(identifier)
        else:
            formatted_identifier = identifier.lower()
        
        # Check rate limiting (3 requests per minute)
        if not rate_limiter.is_allowed(formatted_identifier, max_requests=3, window_minutes=1):
            remaining_time = rate_limiter.get_remaining_time(formatted_identifier)
            return jsonify({
                'error': f'Слишком много запросов. Подождите {remaining_time} секунд перед повторной отправкой'
            }), 429
        
        # Find user
        user = User.find_by_identifier(formatted_identifier)
        is_new_user = user is None
        
        # Generate new code (force create)
        verification_code, plain_code = Code.create_code(formatted_identifier, identifier_type, user.id if user else None)
        db.session.add(verification_code)
        db.session.commit()
        
        # Send code
        if identifier_type == 'phone':
            # SMS sending
            logger.info(f"Force sending SMS to {formatted_identifier} with code {plain_code}")
            success = sms_service.send_verification_code(formatted_identifier, plain_code)
            logger.info(f"SMS sending result: {success}")
            # Also log for test number
            if formatted_identifier == '+77019990438':  # Test number
                logger.info(f"TEST SMS CODE for {formatted_identifier}: {plain_code}")
        else:
            # Email sending
            success = email_service.send_verification_code(formatted_identifier, plain_code)
        
        if not success:
            # If sending failed, remove the code
            db.session.delete(verification_code)
            db.session.commit()
            return jsonify({
                'error': f'Failed to send {identifier_type} verification code'
            }), 500
        
        return jsonify({
            'success': True,
            'identifier': formatted_identifier,
            'type': identifier_type,
            'is_new_user': is_new_user,
            'message': f'Verification code sent to {identifier_type}'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in force_send_code: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@unified_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh JWT access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find user
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new access token
        new_access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'access_token': new_access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in refresh: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
