import requests
import random
import string
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
from .error_handler import auth_error_handler, retry_on_failure

logger = logging.getLogger(__name__)

class MobizonSMSService:
    """
    SMS service for sending verification codes via Mobizon API
    """
    
    def __init__(self):
        self.api_key = os.getenv('MOBIZON_API_KEY')
        if not self.api_key:
            logger.warning("MOBIZON_API_KEY not set in environment variables")
        # Correct Mobizon API endpoint according to documentation
        self.base_url = 'https://api.mobizon.kz/service/message/sendsmsmessage'
        self.timeout = int(os.getenv('SMS_SERVICE_TIMEOUT', '30'))
        self.debug_mode = os.getenv('SMS_DEBUG_MODE', 'false').lower() == 'true'
        
    def generate_verification_code(self, length: int = 6) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number to international format"""
        # Remove all non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Add +7 if phone starts with 7 or 8
        if phone.startswith('7') and len(phone) == 11:
            return f"+{phone}"
        elif phone.startswith('8') and len(phone) == 11:
            return f"+7{phone[1:]}"
        elif phone.startswith('77') and len(phone) == 11:
            return f"+{phone}"
        else:
            # Assume it's already in correct format or add +7
            if not phone.startswith('+'):
                if len(phone) == 10:
                    return f"+7{phone}"
                elif len(phone) == 11 and phone.startswith('7'):
                    return f"+{phone}"
        
        return phone if phone.startswith('+') else f"+{phone}"
    
    def _send_sms_request(self, formatted_phone: str, message: str) -> Dict[str, Any]:
        """
        Internal method to send SMS request to Mobizon API with retry logic
        
        Args:
            formatted_phone: Phone number in international format
            message: SMS message text
            
        Returns:
            Dictionary with send result
        """
        # Mobizon API parameters according to documentation
        params = {
            'apiKey': self.api_key,
            'recipient': formatted_phone.replace('+', ''),  # Remove + for Mobizon
            'text': message
        }
        
        logger.info(f"📱 SMS Request: Sending SMS to {formatted_phone}")
        logger.info(f"📱 SMS Request: Mobizon API URL: {self.base_url}")
        logger.info(f"📱 SMS Request: Mobizon API params: {params}")
        
        # Send request to Mobizon API
        response = requests.post(self.base_url, data=params, timeout=self.timeout)
        
        logger.info(f"📱 SMS Response: Status {response.status_code}")
        logger.info(f"📱 SMS Response: Text {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"📱 SMS Response: JSON {result}")
            
            # Check if the response indicates success
            if result.get('code') == 0:  # Success according to Mobizon API
                logger.info(f"✅ SMS Success: Sent to {formatted_phone}, Message ID: {result.get('data', {}).get('messageId')}")
                return {
                    'success': True,
                    'message': 'SMS sent successfully',
                    'message_id': result.get('data', {}).get('messageId'),
                    'phone': formatted_phone
                }
            else:
                error_msg = result.get('message', 'Unknown error')
                error_code = result.get('code', 'Unknown code')
                logger.error(f"❌ SMS Error: Mobizon API error {error_code} - {error_msg}")
                raise Exception(f"Mobizon API error {error_code}: {error_msg}")
        else:
            logger.error(f"❌ SMS Error: HTTP {response.status_code}: {response.text}")
            raise Exception(f"HTTP error: {response.status_code} - {response.text}")

    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    def send_verification_sms(self, phone: str, code: str) -> Dict[str, Any]:
        """
        Send verification SMS via Mobizon API with retry logic
        
        Args:
            phone: Phone number in international format
            code: Verification code to send
            
        Returns:
            Dictionary with send result
        """
        try:
            formatted_phone = self.format_phone_number(phone)
            
            # Message text in Russian
            message = f"Ваш код подтверждения: {code}. Не сообщайте его никому."
            
            # Debug mode - skip actual SMS sending
            if self.debug_mode:
                logger.info(f"DEBUG MODE: SMS would be sent to {formatted_phone} with code {code}")
                logger.info(f"DEBUG MODE: Message: {message}")
                return {
                    'success': True,
                    'message': 'SMS sent successfully (DEBUG MODE)',
                    'message_id': 'debug-' + str(hash(code)),
                    'phone': formatted_phone,
                    'code': code
                }
            
            # Send SMS with retry logic
            result = self._send_sms_request(formatted_phone, message)
            result['code'] = code
            return result
                
        except requests.exceptions.Timeout as e:
            logger.error(f"SMS API request timeout for {phone}: {str(e)}")
            return auth_error_handler.handle_sms_error(e, phone, "SMS send timeout")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"SMS API connection error for {phone}: {str(e)}")
            return auth_error_handler.handle_sms_error(e, phone, "SMS connection error")
        except Exception as e:
            logger.error(f"Error sending SMS to {phone}: {str(e)}")
            return auth_error_handler.handle_sms_error(e, phone, "SMS send error")
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate if phone number is in correct format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            formatted = self.format_phone_number(phone)
            # Check if it's a valid Kazakhstani number
            return (
                formatted.startswith('+7') and 
                len(formatted) == 12 and 
                formatted[2:].isdigit()
            )
        except:
            return False
    
    def send_verification_code(self, phone: str, code: str) -> bool:
        """
        Send verification code (wrapper for send_verification_sms)
        
        Args:
            phone: Phone number in international format
            code: Verification code to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        result = self.send_verification_sms(phone, code)
        return result['success']


# Global instance
sms_service = MobizonSMSService()

