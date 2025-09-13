import requests
import logging
import os
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from .error_handler import auth_error_handler, retry_on_failure

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """
    Google OAuth service for authentication
    """
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'https://my.ozimiz.org/api/auth/google/callback')
        self.scope = 'openid email profile'
        self.auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        self.token_url = 'https://oauth2.googleapis.com/token'
        self.user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured")
    
    def get_auth_url(self, state: str = None) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
            
        return f"{self.auth_url}?{urlencode(params)}"
    
    def _exchange_code_for_token_request(self, code: str) -> Dict[str, Any]:
        """
        Internal method to exchange authorization code for access token
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Dictionary with token information
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        logger.info(f"🔐 Google OAuth: Exchanging code for token")
        logger.info(f"🔐 Google OAuth: Token URL: {self.token_url}")
        logger.info(f"🔐 Google OAuth: Redirect URI: {self.redirect_uri}")
        
        response = requests.post(self.token_url, data=data, timeout=30)
        
        logger.info(f"🔐 Google OAuth: Token response status: {response.status_code}")
        logger.info(f"🔐 Google OAuth: Token response text: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info("✅ Google OAuth: Successfully exchanged code for token")
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type')
            }
        else:
            logger.error(f"❌ Google OAuth Error: Token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")

    @retry_on_failure(max_retries=2, delay=1.0, backoff=2.0)
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token with retry logic
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Dictionary with token information
        """
        try:
            result = self._exchange_code_for_token_request(code)
            return result
                
        except Exception as e:
            logger.error(f"❌ Google OAuth Error: Error exchanging code for token: {str(e)}")
            return auth_error_handler.handle_google_oauth_error(e, "Token exchange")
    
    def _get_user_info_request(self, access_token: str) -> Dict[str, Any]:
        """
        Internal method to get user information from Google API
        
        Args:
            access_token: Google access token
            
        Returns:
            Dictionary with user information
        """
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        logger.info(f"🔐 Google OAuth: Getting user info")
        logger.info(f"🔐 Google OAuth: User info URL: {self.user_info_url}")
        
        response = requests.get(self.user_info_url, headers=headers, timeout=30)
        
        logger.info(f"🔐 Google OAuth: User info response status: {response.status_code}")
        logger.info(f"🔐 Google OAuth: User info response text: {response.text}")
        
        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"✅ Google OAuth: Successfully retrieved user info for {user_data.get('email')}")
            return {
                'success': True,
                'user_data': {
                    'google_id': user_data.get('id'),
                    'email': user_data.get('email'),
                    'name': user_data.get('name'),
                    'first_name': user_data.get('given_name'),
                    'last_name': user_data.get('family_name'),
                    'picture': user_data.get('picture'),
                    'verified_email': user_data.get('verified_email', False)
                }
            }
        else:
            logger.error(f"❌ Google OAuth Error: Failed to get user info: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get user info: {response.status_code} - {response.text}")

    @retry_on_failure(max_retries=2, delay=1.0, backoff=2.0)
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google API with retry logic
        
        Args:
            access_token: Google access token
            
        Returns:
            Dictionary with user information
        """
        try:
            result = self._get_user_info_request(access_token)
            return result
                
        except Exception as e:
            logger.error(f"❌ Google OAuth Error: Error getting user info: {str(e)}")
            return auth_error_handler.handle_google_oauth_error(e, "User info retrieval")
    
    def is_configured(self) -> bool:
        """
        Check if Google OAuth is properly configured
        
        Returns:
            True if configured, False otherwise
        """
        return bool(self.client_id and self.client_secret)


# Global instance
google_oauth_service = GoogleOAuthService()



