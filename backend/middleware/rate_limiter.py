import time
import asyncio
from collections import defaultdict, deque
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_minute=60, requests_per_hour=1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests = defaultdict(deque)
        self.hour_requests = defaultdict(deque)
        
    def _cleanup_old_requests(self, requests_dict, window_seconds):
        """Remove requests older than the window"""
        current_time = time.time()
        for key in list(requests_dict.keys()):
            while requests_dict[key] and current_time - requests_dict[key][0] > window_seconds:
                requests_dict[key].popleft()
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limits"""
        current_time = time.time()
        
        # Cleanup old requests
        self._cleanup_old_requests(self.minute_requests, 60)
        self._cleanup_old_requests(self.hour_requests, 3600)
        
        # Check minute limit
        if len(self.minute_requests[client_id]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id} (minute)")
            return False
            
        # Check hour limit
        if len(self.hour_requests[client_id]) >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded for {client_id} (hour)")
            return False
        
        # Add current request
        self.minute_requests[client_id].append(current_time)
        self.hour_requests[client_id].append(current_time)
        
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Extract client ID (IP address or API key)
    client_id = request.headers.get("Authorization", request.client.host)
    
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    response = await call_next(request)
    return response 