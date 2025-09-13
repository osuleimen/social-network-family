"""
Centralized error handler for authentication services
"""
import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class AuthErrorHandler:
    """
    Centralized error handler for authentication operations
    """
    
    @staticmethod
    def handle_sms_error(error: Exception, phone: str, operation: str = "SMS operation") -> Dict[str, Any]:
        """
        Handle SMS-related errors with user-friendly messages
        
        Args:
            error: The exception that occurred
            phone: Phone number being processed
            operation: Description of the operation
            
        Returns:
            Dictionary with error information
        """
        error_msg = str(error)
        logger.error(f"SMS {operation} failed for {phone}: {error_msg}")
        
        # Check for specific error types
        if "timeout" in error_msg.lower():
            return {
                'success': False,
                'error': 'Сервис SMS временно недоступен, попробуйте позже',
                'user_message': 'Сервис SMS временно недоступен, попробуйте позже',
                'error_type': 'timeout',
                'phone': phone
            }
        elif "connection" in error_msg.lower():
            return {
                'success': False,
                'error': 'Сервис SMS временно недоступен, попробуйте позже',
                'user_message': 'Сервис SMS временно недоступен, попробуйте позже',
                'error_type': 'connection',
                'phone': phone
            }
        elif "api" in error_msg.lower() or "mobizon" in error_msg.lower():
            return {
                'success': False,
                'error': 'Сервис SMS временно недоступен, попробуйте позже',
                'user_message': 'Сервис SMS временно недоступен, попробуйте позже',
                'error_type': 'api_error',
                'phone': phone
            }
        else:
            return {
                'success': False,
                'error': 'Сервис SMS временно недоступен, попробуйте позже',
                'user_message': 'Сервис SMS временно недоступен, попробуйте позже',
                'error_type': 'unknown',
                'phone': phone
            }
    
    @staticmethod
    def handle_email_error(error: Exception, email: str, operation: str = "Email operation") -> Dict[str, Any]:
        """
        Handle email-related errors with user-friendly messages
        
        Args:
            error: The exception that occurred
            email: Email address being processed
            operation: Description of the operation
            
        Returns:
            Dictionary with error information
        """
        error_msg = str(error)
        logger.error(f"Email {operation} failed for {email}: {error_msg}")
        
        # Check for specific error types
        if "smtp" in error_msg.lower() or "connection" in error_msg.lower():
            return {
                'success': False,
                'error': 'Ошибка при отправке письма, попробуйте позже',
                'user_message': 'Ошибка при отправке письма, попробуйте позже',
                'error_type': 'smtp_error',
                'email': email
            }
        elif "timeout" in error_msg.lower():
            return {
                'success': False,
                'error': 'Ошибка при отправке письма, попробуйте позже',
                'user_message': 'Ошибка при отправке письма, попробуйте позже',
                'error_type': 'timeout',
                'email': email
            }
        else:
            return {
                'success': False,
                'error': 'Ошибка при отправке письма, попробуйте позже',
                'user_message': 'Ошибка при отправке письма, попробуйте позже',
                'error_type': 'unknown',
                'email': email
            }
    
    @staticmethod
    def handle_google_oauth_error(error: Exception, operation: str = "Google OAuth operation") -> Dict[str, Any]:
        """
        Handle Google OAuth-related errors with user-friendly messages
        
        Args:
            error: The exception that occurred
            operation: Description of the operation
            
        Returns:
            Dictionary with error information
        """
        error_msg = str(error)
        logger.error(f"Google OAuth {operation} failed: {error_msg}")
        
        # Check for specific error types
        if "token" in error_msg.lower() or "authorization" in error_msg.lower():
            return {
                'success': False,
                'error': 'Не удалось войти через Google, попробуйте снова',
                'user_message': 'Не удалось войти через Google, попробуйте снова',
                'error_type': 'token_error'
            }
        elif "callback" in error_msg.lower() or "redirect" in error_msg.lower():
            return {
                'success': False,
                'error': 'Не удалось войти через Google, попробуйте снова',
                'user_message': 'Не удалось войти через Google, попробуйте снова',
                'error_type': 'callback_error'
            }
        else:
            return {
                'success': False,
                'error': 'Не удалось войти через Google, попробуйте снова',
                'user_message': 'Не удалось войти через Google, попробуйте снова',
                'error_type': 'unknown'
            }
    
    @staticmethod
    def log_operation_result(operation: str, success: bool, details: Dict[str, Any]):
        """
        Log operation results for debugging
        
        Args:
            operation: Name of the operation
            success: Whether the operation was successful
            details: Additional details about the operation
        """
        if success:
            logger.info(f"{operation} completed successfully: {details}")
        else:
            logger.error(f"{operation} failed: {details}")

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry operations on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt + 1}")
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} failed on attempt {attempt + 1}: {str(e)}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {str(e)}")
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator

# Global instance
auth_error_handler = AuthErrorHandler()

