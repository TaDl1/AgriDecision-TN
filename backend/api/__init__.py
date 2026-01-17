"""
API package initialization and blueprint registration
"""
from flask import Blueprint
from .auth import auth_bp
from .crops import crops_bp
from .decisions import decisions_bp
from .analytics import analytics_bp
from .health import health_bp
from .docs import docs_bp
from .voice import voice_bp


def register_blueprints(app):
    """Register all API blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(crops_bp, url_prefix='/api/crops')
    app.register_blueprint(decisions_bp, url_prefix='/api/decisions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(docs_bp, url_prefix='/api/docs')
    app.register_blueprint(voice_bp, url_prefix='/api/voice')