from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User, PhoneVerification
from app.services.sms_service import sms_service
from app import db
import logging
import re

logger = logging.getLogger(__name__)

sms_auth_bp = Blueprint('sms_auth', __name__)

def validate_phone_format(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Kazakhstani number
    if len(phone_digits) == 11 and phone_digits.startswith('7'):
        return True
    elif len(phone_digits) == 10:
        return True
    
    return False

@sms_auth_bp.route('/request-code', methods=['POST'])
def request_verification_code():
    """Request SMS verification code for phone number"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number', '').strip()
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        # Validate phone number format
        if not validate_phone_format(phone_number):
            return jsonify({'error': 'Invalid phone number format. Use format: +77019990438'}), 400
        
        # Format phone number
        formatted_phone = sms_service.format_phone_number(phone_number)
        
        if not sms_service.validate_phone_number(formatted_phone):
            return jsonify({'error': 'Invalid Kazakhstani phone number'}), 400
        
        # Check if user exists
        existing_user = User.find_by_phone(formatted_phone)
        
        if existing_user:
            # Для существующих пользователей - проверяем, есть ли неистекший код
            existing_verification = PhoneVerification.get_latest_for_phone(formatted_phone)
            
            if existing_verification and existing_verification.is_valid:
                # Есть действующий неиспользованный код - ждем его ввода
                response_data = {
                    'message': 'Existing user - please enter previous SMS code',
                    'phone_number': formatted_phone,
                    'is_new_user': False,
                    'has_existing_code': True,
                    'expires_in': 600
                }
                return jsonify(response_data), 200
            else:
                # Нет неистекшего кода - нужно отправить новый
                # Generate verification code
                verification_code = sms_service.generate_verification_code()
                
                # Delete old verification codes for this phone
                old_codes = PhoneVerification.query.filter_by(phone_number=formatted_phone).all()
                for code in old_codes:
                    db.session.delete(code)
                
                # Create new verification record
                verification = PhoneVerification(
                    phone_number=formatted_phone,
                    verification_code=verification_code,
                    expires_in_minutes=10
                )
                
                db.session.add(verification)
                db.session.commit()
                
                # Send SMS
                sms_result = sms_service.send_verification_sms(formatted_phone, verification_code)
                
                if sms_result['success']:
                    response_data = {
                        'message': 'New verification code sent for existing user',
                        'phone_number': formatted_phone,
                        'is_new_user': False,
                        'has_existing_code': False,
                        'expires_in': 600
                    }
                    
                    # Показываем код в debug режиме
                    if sms_service.debug_mode:
                        response_data['code'] = verification_code
                        
                    return jsonify(response_data), 200
                else:
                    logger.error(f"SMS send failed: {sms_result.get('error')}")
                    return jsonify({
                        'message': 'Verification code sent successfully',
                        'phone_number': formatted_phone,
                        'is_new_user': False,
                        'expires_in': 600
                    }), 200
            
        else:
            # Generate verification code
            verification_code = sms_service.generate_verification_code()
            
            # Delete old verification codes for this phone
            old_codes = PhoneVerification.query.filter_by(phone_number=formatted_phone).all()
            for code in old_codes:
                db.session.delete(code)
            
            # Create new verification record
            verification = PhoneVerification(
                phone_number=formatted_phone,
                verification_code=verification_code,
                expires_in_minutes=10
            )
            
            db.session.add(verification)
            db.session.commit()
            
            # Send SMS
            sms_result = sms_service.send_verification_sms(formatted_phone, verification_code)
            
            if sms_result['success']:
                response_data = {
                    'message': 'Verification code sent successfully',
                    'phone_number': formatted_phone,
                    'is_new_user': existing_user is None,
                    'expires_in': 600  # 10 minutes in seconds
                }
                
                # Показываем код в debug режиме
                if sms_service.debug_mode:
                    response_data['code'] = verification_code
                    
                return jsonify(response_data), 200
            else:
                # If SMS failed, still return success to prevent phone number enumeration
                logger.error(f"SMS send failed: {sms_result.get('error')}")
                return jsonify({
                    'message': 'Verification code sent successfully',
                    'phone_number': formatted_phone,
                    'is_new_user': existing_user is None,
                    'expires_in': 600
                }), 200
            
    except Exception as e:
        logger.error(f"Error in request_verification_code: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@sms_auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    """Verify SMS code and authenticate user"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number', '').strip()
        verification_code = data.get('verification_code', '').strip()
        
        if not phone_number or not verification_code:
            return jsonify({'error': 'Phone number and verification code are required'}), 400
        
        # Format phone number
        formatted_phone = sms_service.format_phone_number(phone_number)
        
        # Find latest verification code for this phone
        verification = PhoneVerification.get_latest_for_phone(formatted_phone)
        
        if not verification:
            return jsonify({'error': 'No verification code found. Please request a new one.'}), 400
        
        if not verification.is_valid:
            if verification.is_expired:
                return jsonify({'error': 'Verification code has expired. Please request a new one.'}), 400
            elif verification.attempts >= 5:
                return jsonify({'error': 'Too many failed attempts. Please request a new code.'}), 400
            else:
                return jsonify({'error': 'Verification code is no longer valid.'}), 400
        
        # Verify the code
        if verification.verify(verification_code):
            # Code is correct
            db.session.commit()
            
            # Find or create user
            user = User.find_by_phone(formatted_phone)
            
            if not user:
                # Create new user
                user = User.create_from_phone(
                    phone_number=formatted_phone,
                    first_name='Пользователь',  # Default name
                    last_name='',
                    is_verified=True
                )
                db.session.add(user)
                db.session.commit()
                
                logger.info(f"Created new user for phone {formatted_phone}")
                is_new_user = True
            else:
                logger.info(f"User {user.id} authenticated via SMS")
                is_new_user = False
            
            # Generate JWT tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            # Clean up verification record
            db.session.delete(verification)
            db.session.commit()
            
            return jsonify({
                'message': 'Authentication successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(),
                'is_new_user': is_new_user
            }), 200
            
        else:
            # Wrong code
            db.session.commit()
            remaining_attempts = 5 - verification.attempts
            
            return jsonify({
                'error': 'Invalid verification code',
                'remaining_attempts': remaining_attempts
            }), 400
            
    except Exception as e:
        logger.error(f"Error in verify_code: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@sms_auth_bp.route('/resend-code', methods=['POST'])
def resend_verification_code():
    """Resend verification code"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number', '').strip()
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        # Format phone number
        formatted_phone = sms_service.format_phone_number(phone_number)
        
        # Check if we can resend (rate limiting)
        latest_verification = PhoneVerification.get_latest_for_phone(formatted_phone)
        
        if latest_verification and not latest_verification.is_expired:
            # Check if enough time has passed (e.g., 60 seconds)
            from datetime import datetime, timedelta
            if datetime.utcnow() - latest_verification.created_at < timedelta(seconds=60):
                return jsonify({'error': 'Please wait before requesting a new code'}), 429
        
        # Use the same logic as request-code
        return request_verification_code()
        
    except Exception as e:
        logger.error(f"Error in resend_verification_code: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

