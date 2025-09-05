import requests
import random
import string
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class MobizonSMSService:
    """
    SMS service for sending verification codes via Mobizon API
    """
    
    def __init__(self):
        self.api_key = os.getenv('MOBIZON_API_KEY')
        if not self.api_key:
            logger.warning("MOBIZON_API_KEY not set in environment variables")
        self.base_url = 'https://api.mobizon.kz/service/message/sendsmsmessage'
        self.timeout = int(os.getenv('SMS_SERVICE_TIMEOUT', '30'))
        self.debug_mode = os.getenv('SMS_DEBUG_MODE', 'false').lower() == 'true'
        
    def generate_verification_code(self, length: int = 4) -> str:
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
    
    def send_verification_sms(self, phone: str, code: str) -> Dict[str, Any]:
        """
        Send verification SMS via Mobizon API
        
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
            
            # Mobizon API parameters
            params = {
                'apiKey': self.api_key,
                'recipient': formatted_phone.replace('+', ''),  # Убираем + для Mobizon
                'text': message
            }
            
            logger.info(f"Sending SMS to {formatted_phone} with code {code}")
            logger.info(f"Mobizon API URL: {self.base_url}")
            logger.info(f"Mobizon API params: {params}")
            
            # Send request to Mobizon API
            response = requests.post(self.base_url, data=params, timeout=self.timeout)
            
            logger.info(f"Mobizon API response status: {response.status_code}")
            logger.info(f"Mobizon API response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 0:  # Success
                    logger.info(f"SMS sent successfully to {formatted_phone}")
                    return {
                        'success': True,
                        'message': 'SMS sent successfully',
                        'message_id': result.get('data', {}).get('messageId'),
                        'phone': formatted_phone,
                        'code': code
                    }
                else:
                    error_msg = result.get('message', 'Unknown error')
                    logger.error(f"Mobizon API error: {error_msg}")
                    return {
                        'success': False,
                        'error': f"SMS API error: {error_msg}",
                        'phone': formatted_phone
                    }
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP error: {response.status_code}",
                    'phone': formatted_phone
                }
                
        except requests.exceptions.Timeout:
            logger.error("SMS API request timeout")
            return {
                'success': False,
                'error': 'SMS service timeout',
                'phone': phone
            }
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return {
                'success': False,
                'error': f"SMS send error: {str(e)}",
                'phone': phone
            }
    
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


# Global instance
sms_service = MobizonSMSService()

