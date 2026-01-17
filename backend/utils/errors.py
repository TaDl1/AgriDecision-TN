"""
Custom exception classes and error handlers
"""
from flask import jsonify


class APIError(Exception):
    """Base exception for API errors"""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = {'status': 'error', 'error': self.message}
        # Include validation details if present
        if self.payload and 'errors' in self.payload:
            rv['payload'] = {'errors': self.payload['errors']}
        return rv


class ValidationError(APIError):
    """Validation error (422)"""
    status_code = 422


class AuthenticationError(APIError):
    """Authentication error (401)"""
    status_code = 401


class AuthorizationError(APIError):
    """Authorization error (403)"""
    status_code = 403


class NotFoundError(APIError):
    """Resource not found (404)"""
    status_code = 404


class ConflictError(APIError):
    """Resource conflict (409)"""
    status_code = 409


class ExternalServiceError(APIError):
    """External service failure (503)"""
    status_code = 503


def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Resource not found',
            'status': 'error'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'error': 'Method not allowed',
            'status': 'error'
        }), 405
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if app.config.get('TESTING'):
            raise error
        app.logger.error(f'Unexpected error: {str(error)}', exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 'error'
        }), 500