"""
Health check endpoints
"""
from flask import Blueprint, jsonify
from models.base import db
from datetime import datetime
import time
import psutil
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('', methods=['GET'])
def health_check():
    """
    Basic health check
    ---
    tags:
      - System
    responses:
      200:
        description: System status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200


@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with dependency status
    ---
    tags:
      - System
    responses:
      200:
        description: Detailed system health
      503:
        description: One or more services unhealthy
    """
    checks = {
        'database': check_database(),
        'weather_api': check_weather_api(),
        'ai_service': check_ai_service()
    }
    
    # Overall status
    all_healthy = all(check['healthy'] for check in checks.values())
    status = 'healthy' if all_healthy else 'unhealthy'
    
    # System metrics
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        system_metrics = {
            'memory_usage_mb': round(memory.used / 1024 / 1024, 2),
            'memory_percent': memory.percent,
            'cpu_percent': cpu_percent
        }
    except:
        system_metrics = {}
    
    return jsonify({
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'checks': checks,
        'system_metrics': system_metrics
    }), 200 if all_healthy else 503


def check_database():
    """Check database connectivity"""
    try:
        start = time.time()
        db.session.execute('SELECT 1')
        duration = (time.time() - start) * 1000
        
        return {
            'healthy': True,
            'message': 'Database connected',
            'response_time_ms': round(duration, 2)
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'healthy': False,
            'message': f'Database error: {str(e)}',
            'response_time_ms': 0
        }


def check_weather_api():
    """Check weather API availability"""
    try:
        from services.weather_service import WeatherService
        service = WeatherService()
        
        start = time.time()
        # Try to get forecast for Tunis
        forecast = service.get_forecast('Tunis', days=1)
        duration = (time.time() - start) * 1000
        
        return {
            'healthy': True,
            'message': 'Weather API responsive',
            'response_time_ms': round(duration, 2)
        }
    except Exception as e:
        logger.error(f"Weather API health check failed: {e}")
        return {
            'healthy': False,
            'message': f'Weather API error: {str(e)}',
            'response_time_ms': 0
        }


def check_ai_service():
    """Check AI service availability"""
    try:
        from services.ai_service import AIService
        service = AIService()
        
        return {
            'healthy': True,
            'message': 'AI service available' if service.enabled else 'AI service disabled (using templates)',
            'enabled': service.enabled
        }
    except Exception as e:
        logger.error(f"AI service health check failed: {e}")
        return {
            'healthy': False,
            'message': f'AI service error: {str(e)}',
            'enabled': False
        }