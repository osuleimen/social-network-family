from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User, EmailVerification
from app.services.email_service import email_service
from app.services.error_handler import auth_error_handler
from app import db
import logging
import re

logger = logging.getLogger(__name__)

email_auth_bp = Blueprint('email_auth', __name__)

def validate_email_format(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@email_auth_bp.route('/email/request-code', methods=['POST'])
def request_verification_code():
    """Request email verification code"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email_format(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user exists
        existing_user = User.find_by_email(email)
        is_new_user = existing_user is None
        
        # Check for existing valid verification
        existing_verification = EmailVerification.get_latest_for_email(email)
        has_existing_code = existing_verification is not None
        
        if has_existing_code:
            # User has a valid code, don't send new one
            return jsonify({
                'message': 'Verification code already sent',
                'email': email,
                'is_new_user': is_new_user,
                'has_existing_code': True
            }), 200
        
        # Generate verification code
        verification_code = email_service.generate_verification_code()
        
        # Invalidate old verifications
        EmailVerification.invalidate_old_verifications(email)
        
        # Create new verification record
        verification = EmailVerification.create_verification(email, verification_code)
        db.session.add(verification)
        db.session.commit()
        
        # Send email
        result = email_service.send_verification_email(email, verification_code)
        
        if result['success']:
            logger.info(f"Email verification code sent to {email}")
            return jsonify({
                'message': 'Verification code sent successfully',
                'email': email,
                'is_new_user': is_new_user,
                'has_existing_code': False
            }), 200
        else:
            # Clean up verification record if email failed
            db.session.delete(verification)
            db.session.commit()
            
            logger.error(f"Failed to send email to {email}: {result.get('error')}")
            return jsonify({'error': result.get('user_message', 'Не удалось отправить письмо, попробуйте позже')}), 500
            
    except Exception as e:
        logger.error(f"❌ Email Auth Error: Error in request_verification_code: {str(e)}")
        error_result = auth_error_handler.handle_email_error(e, email if 'email' in locals() else 'unknown', "Email code request")
        return jsonify({'error': error_result['user_message']}), 500

@email_auth_bp.route('/email/verify-code', methods=['POST'])
def verify_code():
    """Verify email code and authenticate user"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        verification_code = data.get('verification_code', '').strip()
        
        if not email or not verification_code:
            return jsonify({'error': 'Email and verification code are required'}), 400
        
        # Find latest verification code for this email
        verification = EmailVerification.get_latest_for_email(email)
        
        if not verification:
            return jsonify({'error': 'Код подтверждения не найден. Запросите новый код.'}), 400
        
        if not verification.is_valid:
            if verification.attempts >= 5:
                return jsonify({'error': 'Слишком много попыток. Запросите новый код.'}), 400
            else:
                return jsonify({'error': 'Код подтверждения больше не действителен.'}), 400
        
        # Verify the code
        if verification.verify(verification_code):
            # Code is correct
            db.session.commit()
            
            # Find or create user
            user = User.find_by_email(email)
            
            if not user:
                # Create new user
                user = User.create_from_email(
                    email=email,
                    first_name='Пользователь',  # Default name
                    last_name='',
                    is_verified=True
                )
                db.session.add(user)
                db.session.commit()
                
                logger.info(f"Created new user for email {email}")
                is_new_user = True
            else:
                logger.info(f"User {user.id} authenticated via email")
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
                'error': 'Неверный код подтверждения',
                'remaining_attempts': remaining_attempts
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Email Auth Error: Error in verify_code: {str(e)}")
        error_result = auth_error_handler.handle_email_error(e, email if 'email' in locals() else 'unknown', "Email code verification")
        return jsonify({'error': error_result['user_message']}), 500

@email_auth_bp.route('/email/resend-code', methods=['POST'])
def resend_verification_code():
    """Resend verification code"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email_format(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Invalidate existing verifications
        EmailVerification.invalidate_old_verifications(email)
        
        # Generate new verification code
        verification_code = email_service.generate_verification_code()
        
        # Create new verification record
        verification = EmailVerification.create_verification(email, verification_code)
        db.session.add(verification)
        db.session.commit()
        
        # Send email
        result = email_service.send_verification_email(email, verification_code)
        
        if result['success']:
            logger.info(f"Email verification code resent to {email}")
            return jsonify({
                'message': 'Verification code resent successfully',
                'email': email
            }), 200
        else:
            # Clean up verification record if email failed
            db.session.delete(verification)
            db.session.commit()
            
            logger.error(f"Failed to resend email to {email}: {result.get('error')}")
            return jsonify({'error': result.get('user_message', 'Не удалось отправить письмо, попробуйте позже')}), 500
            
    except Exception as e:
        logger.error(f"❌ Email Auth Error: Error in resend_verification_code: {str(e)}")
        error_result = auth_error_handler.handle_email_error(e, email if 'email' in locals() else 'unknown', "Email code resend")
        return jsonify({'error': error_result['user_message']}), 500
