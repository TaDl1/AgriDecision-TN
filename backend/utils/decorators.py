"""
Custom decorators for API endpoints
"""
from functools import wraps
from flask import request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt
import time
from utils.errors import ValidationError, AuthorizationError


def validate_json(*required_fields):
    """Validate JSON request body has required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError('Request must be JSON')
            
            data = request.get_json()
            if not data:
                raise ValidationError('Request body cannot be empty')
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(
                    f'Missing required fields: {", ".join(missing_fields)}'
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Require admin role for endpoint access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'admin':
            raise AuthorizationError('Admin access required')
        
        return f(*args, **kwargs)
    return decorated_function


def track_performance(f):
    """Track endpoint performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        g.request_duration = end_time - start_time
        return result
    return decorated_function


def cache_response(timeout=300):
    """Cache GET request responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            from flask import current_app
            
            # Get cache from extensions, or use a simple dict-based cache
            try:
                cache = current_app.extensions.get('cache')
                if not cache or isinstance(cache, dict):
                    # Skip caching if cache not properly initialized
                    return f(*args, **kwargs)
                
                cache_key = f'{f.__name__}:{str(args)}:{str(kwargs)}:{str(request.args)}'
                cached_response = cache.get(cache_key)
                
                if cached_response is not None:
                    return cached_response
                
                response = f(*args, **kwargs)
                cache.set(cache_key, response, timeout=timeout)
                return response
            except Exception as e:
                # If caching fails, just return the response without caching
                import logging
                logging.warning(f"Cache operation failed: {e}")
                return f(*args, **kwargs)
        return decorated_function
    return decorator