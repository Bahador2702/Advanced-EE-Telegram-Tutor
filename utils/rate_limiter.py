import time
from collections import defaultdict
from typing import Dict, Tuple


class RateLimiter:
    """Simple per-user rate limiter"""
    
    def __init__(self, max_requests: int, period_seconds: int):
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self.requests: Dict[int, list] = defaultdict(list)
    
    def check(self, user_id: int) -> bool:
        """Return True if request is allowed, False if rate limited"""
        now = time.time()
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.period_seconds
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[user_id].append(now)
        return True
    
    def reset(self, user_id: int):
        """Reset rate limit for a user"""
        if user_id in self.requests:
            self.requests[user_id] = []