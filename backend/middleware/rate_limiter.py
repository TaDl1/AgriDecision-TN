"""
Rate limiting configuration
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def setup_rate_limiting(app):
    """Configure rate limiting for the application"""
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per day", "10 per minute"],
        storage_uri="memory://",
        headers_enabled=True
    )
    
    return limiter