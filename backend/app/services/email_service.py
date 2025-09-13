from flask import current_app
from flask_mail import Message
from app import mail
import logging
import os
import random
import string
from typing import Dict, Any
from .error_handler import auth_error_handler, retry_on_failure

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.debug_mode = os.environ.get('EMAIL_DEBUG_MODE', 'false').lower() == 'true'
    
    def generate_verification_code(self, length: int = 6) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def _send_email_request(self, email: str, code: str) -> Dict[str, Any]:
        """
        Internal method to send email request with detailed logging
        
        Args:
            email: Email address to send to
            code: Verification code
            
        Returns:
            Dictionary with send result
        """
        try:
            # Log SMTP configuration for debugging
            logger.info(f"📧 Email Config: SMTP Configuration:")
            logger.info(f"📧 Email Config:   Server: {current_app.config.get('MAIL_SERVER', 'Not set')}")
            logger.info(f"📧 Email Config:   Port: {current_app.config.get('MAIL_PORT', 'Not set')}")
            logger.info(f"📧 Email Config:   Use TLS: {current_app.config.get('MAIL_USE_TLS', 'Not set')}")
            logger.info(f"📧 Email Config:   Use SSL: {current_app.config.get('MAIL_USE_SSL', 'Not set')}")
            logger.info(f"📧 Email Config:   Username: {current_app.config.get('MAIL_USERNAME', 'Not set')}")
            logger.info(f"📧 Email Config:   Default Sender: {current_app.config.get('MAIL_DEFAULT_SENDER', 'Not set')}")
            
            msg = Message(
                subject='Код подтверждения - OZIMIZ',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            
            msg.html = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2563eb;">Код подтверждения</h2>
                    <p>Здравствуйте!</p>
                    <p>Ваш код подтверждения для входа в OZIMIZ:</p>
                    <div style="background-color: #f3f4f6; padding: 20px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #1f2937; font-size: 32px; letter-spacing: 8px; margin: 0;">{code}</h1>
                    </div>
                    <p>Код действителен до запроса нового.</p>
                    <p>Если вы не запрашивали этот код, проигнорируйте это сообщение.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="color: #6b7280; font-size: 12px;">
                        С уважением,<br>
                        Команда OZIMIZ
                    </p>
                </div>
            </body>
            </html>
            """
            
            logger.info(f"📧 Email Send: Attempting to send email to {email}")
            mail.send(msg)
            logger.info(f"✅ Email Success: Sent to {email}")
            
            return {
                'success': True,
                'message': 'Email sent successfully',
                'email': email,
                'code': code
            }
            
        except Exception as e:
            logger.error(f"❌ Email Error: Failed to send email to {email}: {str(e)}")
            raise e

    @retry_on_failure(max_retries=2, delay=2.0, backoff=2.0)
    def send_verification_email(self, email: str, code: str) -> Dict[str, Any]:
        """
        Send verification code via email with retry logic and comprehensive logging
        
        Args:
            email: Email address to send to
            code: Verification code
            
        Returns:
            Dictionary with send result
        """
        try:
            if self.debug_mode:
                logger.info(f"DEBUG MODE: Email code for {email}: {code}")
                return {
                    'success': True,
                    'message': 'Email sent successfully (DEBUG MODE)',
                    'email': email,
                    'code': code
                }
            
            # Send email with retry logic
            result = self._send_email_request(email, code)
            return result
            
        except Exception as e:
            logger.error(f"Error sending email to {email}: {str(e)}")
            return auth_error_handler.handle_email_error(e, email, "Email send error")

    def send_verification_code(self, email: str, code: str) -> bool:
        """
        Legacy method for backward compatibility
        
        Args:
            email: Email address to send to
            code: Verification code
            
        Returns:
            True if sent successfully, False otherwise
        """
        result = self.send_verification_email(email, code)
        return result['success']

# Create singleton instance
email_service = EmailService()