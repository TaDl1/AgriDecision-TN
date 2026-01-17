"""
Main Flask application factory
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from pathlib import Path
from flasgger import Swagger

# Load environment variables
load_dotenv()

# Import models and services
from models.base import db
from config import config
from utils.logger import setup_logger, RequestLogger
from utils.errors import register_error_handlers
from middleware.performance import PerformanceMonitor

# Setup logger
logger = setup_logger(__name__)

# Initialize extensions
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure data and logs directories exist
    data_dir = Path(app.root_path) / 'data'
    logs_dir = Path(app.root_path) / 'logs'
    data_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    # Swagger Configuration for JWT
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "AgriDecision-TN API",
            "description": "API for Tunisian Smart Farming Decision Support System",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "bearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
            }
        }
    }
    Swagger(app, template=swagger_template) # Automated API Documentation
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register middleware
    RequestLogger(app)
    PerformanceMonitor(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register API Blueprints
    from api import register_blueprints
    register_blueprints(app)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'AgriDecision-TN API',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': {
                'auth': '/api/auth',
                'crops': '/api/crops',
                'decisions': '/api/decisions',
                'analytics': '/api/analytics',
                'health': '/api/health',
                'docs': '/api/docs'
            }
        }), 200
    
    # Database initialization
    with app.app_context():
        try:
            db.create_all()
            logger.info('Database tables created successfully')
            
            # Initialize seed data
            from services.init_db import init_database
            try:
                init_database()
                logger.info('Database seeded successfully')
            except Exception as e:
                logger.warning(f'Database seeding skipped (already populated): {e}')
        
        except Exception as e:
            logger.error(f'Database initialization error: {e}', exc_info=True)
    
    logger.info(f'Application started in {config_name} mode')
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        host='127.0.0.1',
        port=port,
        debug=debug,
        use_reloader=debug
    )