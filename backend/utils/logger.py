"""
Centralized logging configuration
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os


def setup_logger(name: str, log_file: str = 'logs/app.log', level=logging.INFO):
    """Setup comprehensive logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / Path(log_file).name
    
    # File Handler
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    file_handler.setLevel(level)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    console_handler.setLevel(level)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class RequestLogger:
    """Middleware for logging HTTP requests"""
    
    def __init__(self, app=None):
        self.logger = setup_logger('requests')
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        @app.before_request
        def log_request():
            from flask import request
            self.logger.info(
                f'{request.method} {request.path} from {request.remote_addr}'
            )
        
        @app.after_request
        def log_response(response):
            from flask import request, g
            duration = getattr(g, 'request_duration', 0)
            self.logger.info(
                f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s'
            )
            return response