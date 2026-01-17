"""
Performance monitoring middleware
"""
import time
from flask import g, request
from utils.logger import setup_logger

logger = setup_logger('performance')


class PerformanceMonitor:
    """Monitor request performance and log metrics"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Store request start time"""
        g.start_time = time.time()
        g.request_start = time.perf_counter()
    
    def after_request(self, response):
        """Calculate and log request duration"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            g.request_duration = duration
            
            # Add timing header
            response.headers['X-Request-Duration'] = f'{duration:.4f}s'
            
            # Log slow requests (>2 seconds)
            if duration > 2.0:
                logger.warning(
                    f'SLOW REQUEST: {request.method} {request.path} took {duration:.2f}s'
                )
        
        return response


class RequestCounter:
    """Count and track API usage"""
    
    def __init__(self):
        self.request_count = {}
        self.error_count = {}
    
    def increment(self, endpoint, is_error=False):
        """Increment request counter for endpoint"""
        if endpoint not in self.request_count:
            self.request_count[endpoint] = 0
            self.error_count[endpoint] = 0
        
        self.request_count[endpoint] += 1
        if is_error:
            self.error_count[endpoint] += 1
    
    def get_stats(self):
        """Get usage statistics"""
        total = sum(self.request_count.values())
        total_errors = sum(self.error_count.values())
        
        return {
            'total_requests': total,
            'total_errors': total_errors,
            'error_rate': (total_errors / total * 100) if total > 0 else 0,
            'by_endpoint': self.request_count,
            'errors_by_endpoint': self.error_count,
            'top_endpoints': sorted(
                self.request_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }