import time
import psutil
import threading
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class APIMonitor:
    """Monitor API performance and system health"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        
    def record_request(self, response_time: float, success: bool = True):
        """Record a request with its response time"""
        with self.lock:
            self.request_count += 1
            self.total_response_time += response_time
            if not success:
                self.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current API statistics"""
        with self.lock:
            uptime = time.time() - self.start_time
            avg_response_time = (
                self.total_response_time / self.request_count 
                if self.request_count > 0 else 0
            )
            error_rate = (
                self.error_count / self.request_count * 100 
                if self.request_count > 0 else 0
            )
            
            return {
                "uptime_seconds": uptime,
                "total_requests": self.request_count,
                "error_count": self.error_count,
                "error_rate_percent": error_rate,
                "avg_response_time_seconds": avg_response_time,
                "requests_per_second": self.request_count / uptime if uptime > 0 else 0
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "percent_used": memory.percent
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "percent_used": (disk.used / disk.total) * 100
                },
                "cpu_percent": cpu_percent
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"error": str(e)}

# Global monitor instance
api_monitor = APIMonitor() 