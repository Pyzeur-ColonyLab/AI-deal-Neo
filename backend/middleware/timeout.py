import asyncio
import time
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

class TimeoutMiddleware:
    def __init__(self, timeout_seconds=60):
        self.timeout_seconds = timeout_seconds
    
    async def __call__(self, request: Request, call_next):
        """Timeout middleware implementation"""
        start_time = time.time()
        
        try:
            # Create a task with timeout
            task = asyncio.create_task(call_next(request))
            response = await asyncio.wait_for(task, timeout=self.timeout_seconds)
            
            # Log request duration
            duration = time.time() - start_time
            logger.info(f"Request completed in {duration:.2f}s: {request.method} {request.url.path}")
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {self.timeout_seconds}s: {request.method} {request.url.path}")
            raise HTTPException(
                status_code=408,
                detail=f"Request timeout after {self.timeout_seconds} seconds"
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed after {duration:.2f}s: {str(e)}")
            raise

# Global timeout middleware instance
timeout_middleware = TimeoutMiddleware(timeout_seconds=60) 