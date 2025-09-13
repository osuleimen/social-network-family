from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User, PhoneVerification
from app.services.sms_service import sms_service
from app.services.error_handler import auth_error_handler
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
                # Есть действующий код - используем его
                response_data = {
                    'message': 'Пользователь уже зарегистрирован. Введите код, отправленный ранее, или запросите новый код.',
                    'phone_number': formatted_phone,
                    'is_new_user': False,
                    'has_existing_code': True,
                    'expires_in': 0  # Код не истекает
                }
                
                # Показываем код в debug режиме
                if sms_service.debug_mode:
                    response_data['code'] = existing_verification.verification_code
                    
                return jsonify(response_data), 200
            else:
                # Нет действующего кода - НЕ создаем новый, а говорим пользователю запросить новый код
                response_data = {
                    'message': 'Нет действующего кода. Нажмите "Запросить новый код" для получения SMS.',
                    'phone_number': formatted_phone,
                    'is_new_user': False,
                    'has_existing_code': False,
                    'expires_in': 0
                }
                return jsonify(response_data), 200
            
        else:
            # Проверяем, есть ли уже код для этого номера
            existing_verification = PhoneVerification.get_latest_for_phone(formatted_phone)
            
            if existing_verification and existing_verification.is_valid:
                # Есть действующий код - используем его
                response_data = {
                    'message': 'Код уже существует и действителен',
                    'phone_number': formatted_phone,
                    'is_new_user': True,
                    'has_existing_code': True,
                    'expires_in': 0  # Код не истекает
                }
                
                # Показываем код в debug режиме
                if sms_service.debug_mode:
                    response_data['code'] = existing_verification.verification_code
                    
                return jsonify(response_data), 200
            else:
                # Нет действующего кода - НЕ создаем новый, а говорим пользователю запросить новый код
                response_data = {
                    'message': 'Нет действующего кода. Нажмите "Запросить новый код" для получения SMS.',
                    'phone_number': formatted_phone,
                    'is_new_user': True,
                    'has_existing_code': False,
                    'expires_in': 0
                }
                return jsonify(response_data), 200
            
    except Exception as e:
        logger.error(f"❌ SMS Auth Error: Error in request_verification_code: {str(e)}")
        error_result = auth_error_handler.handle_sms_error(e, phone_number if 'phone_number' in locals() else 'unknown', "SMS code request")
        return jsonify({'error': error_result['user_message']}), 500

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
        
        # Find ALL verification codes for this phone and check each one
        verifications = PhoneVerification.query.filter_by(phone_number=formatted_phone).all()
        
        if not verifications:
            return jsonify({'error': 'Код подтверждения не найден. Запросите новый код.'}), 400
        
        # Check each verification code
        valid_verification = None
        for verification in verifications:
            if verification.is_valid and verification.verification_code == verification_code:
                valid_verification = verification
                break
        
        if not valid_verification:
            # Try to find any code that matches (even if not valid) to increment attempts
            for verification in verifications:
                if verification.verification_code == verification_code:
                    verification.attempts += 1
                    db.session.commit()
                    remaining_attempts = 5 - verification.attempts
                    return jsonify({
                        'error': 'Неверный код подтверждения',
                        'remaining_attempts': remaining_attempts
                    }), 400
            
            return jsonify({'error': 'Неверный код подтверждения'}), 400
        
        # Verify the code
        if valid_verification.verify(verification_code):
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
            
            # НЕ удаляем код верификации - он может использоваться повторно
            db.session.commit()
            
            return jsonify({
                'message': 'Authentication successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(),
                'is_new_user': is_new_user
            }), 200
            
        else:
            # Wrong code - this should not happen as we already checked above
            db.session.commit()
            remaining_attempts = 5 - valid_verification.attempts
            
            return jsonify({
                'error': 'Неверный код подтверждения',
                'remaining_attempts': remaining_attempts
            }), 400
            
    except Exception as e:
        logger.error(f"❌ SMS Auth Error: Error in verify_code: {str(e)}")
        error_result = auth_error_handler.handle_sms_error(e, phone_number if 'phone_number' in locals() else 'unknown', "SMS code verification")
        return jsonify({'error': error_result['user_message']}), 500

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
        
        # Force create new code for resend
        verification_code = sms_service.generate_verification_code()
        
        # Create new verification record
        verification = PhoneVerification(
            phone_number=formatted_phone,
            verification_code=verification_code,
            expires_in_minutes=None  # Код не истекает
        )
        
        db.session.add(verification)
        db.session.commit()
        
        # Send SMS
        sms_result = sms_service.send_verification_sms(formatted_phone, verification_code)
        
        if sms_result['success']:
            response_data = {
                'message': 'Новый код отправлен',
                'phone_number': formatted_phone,
                'expires_in': 0  # Код не истекает
            }
            
            # Показываем код в debug режиме
            if sms_service.debug_mode:
                response_data['code'] = verification_code
                
            return jsonify(response_data), 200
        else:
            logger.error(f"SMS send failed: {sms_result.get('error')}")
            return jsonify({
                'error': sms_result.get('user_message', 'SMS недоступно, попробуйте позже')
            }), 500
        
    except Exception as e:
        logger.error(f"❌ SMS Auth Error: Error in resend_verification_code: {str(e)}")
        error_result = auth_error_handler.handle_sms_error(e, phone_number if 'phone_number' in locals() else 'unknown', "SMS code resend")
        return jsonify({'error': error_result['user_message']}), 500

