from datetime import datetime, timedelta
from typing import Dict, List
import threading

class RateLimiter:
    """
    Simple in-memory rate limiter for authentication requests
    Rate limit: 3 requests per minute per identifier
    """
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str, max_requests: int = 3, window_minutes: int = 1) -> bool:
        """
        Check if request is allowed for the given identifier
        
        Args:
            identifier: Phone number or email
            max_requests: Maximum requests allowed in window
            window_minutes: Time window in minutes
            
        Returns:
            True if request is allowed, False otherwise
        """
        with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            # Get existing requests for this identifier
            requests = self._requests.get(identifier, [])
            
            # Remove old requests outside the window
            requests = [req_time for req_time in requests if req_time > window_start]
            
            # Check if we're under the limit
            if len(requests) < max_requests:
                # Add current request
                requests.append(now)
                self._requests[identifier] = requests
                return True
            else:
                # Update the list (remove old requests)
                self._requests[identifier] = requests
                return False
    
    def get_remaining_time(self, identifier: str, window_minutes: int = 1) -> int:
        """
        Get remaining time in seconds until next request is allowed
        
        Args:
            identifier: Phone number or email
            window_minutes: Time window in minutes
            
        Returns:
            Seconds until next request is allowed
        """
        with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            requests = self._requests.get(identifier, [])
            requests = [req_time for req_time in requests if req_time > window_start]
            
            if len(requests) < 3:
                return 0
            
            # Find the oldest request in the window
            oldest_request = min(requests)
            next_allowed = oldest_request + timedelta(minutes=window_minutes)
            
            remaining_seconds = (next_allowed - now).total_seconds()
            return max(0, int(remaining_seconds))
    
    def cleanup_old_entries(self):
        """Clean up old entries to prevent memory leaks"""
        with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(hours=1)  # Keep only last hour
            
            for identifier in list(self._requests.keys()):
                requests = self._requests[identifier]
                requests = [req_time for req_time in requests if req_time > cutoff]
                
                if requests:
                    self._requests[identifier] = requests
                else:
                    del self._requests[identifier]

# Global rate limiter instance
rate_limiter = RateLimiter()
