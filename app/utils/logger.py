import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import json

class ConfigHubLogger:
    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # Set up backend logger
        backend_logger = logging.getLogger('backend')
        backend_logger.setLevel(logging.DEBUG)

        # Create backend log file handler
        backend_handler = RotatingFileHandler(
            os.path.join(log_dir, 'backend.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        backend_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        backend_handler.setFormatter(backend_formatter)
        backend_logger.addHandler(backend_handler)

        # Set up frontend logger
        frontend_logger = logging.getLogger('frontend')
        frontend_logger.setLevel(logging.DEBUG)

        # Create frontend log file handler
        frontend_handler = RotatingFileHandler(
            os.path.join(log_dir, 'frontend.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        frontend_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        frontend_handler.setFormatter(frontend_formatter)
        frontend_logger.addHandler(frontend_handler)

        # Store loggers
        self.backend_logger = backend_logger
        self.frontend_logger = frontend_logger

    def log_frontend(self, logs):
        """Log frontend messages to frontend.log"""
        for log in logs:
            level = getattr(logging, log['level'].upper(), logging.INFO)
            message = f"[{log['component']}] {log['message']}"
            if log['data']:
                message += f" - Data: {log['data']}"
            self.frontend_logger.log(level, message)

    def debug(self, component, message, **kwargs):
        """Log debug message with component name"""
        self._log('debug', component, message, **kwargs)

    def info(self, component, message, **kwargs):
        """Log info message with component name"""
        self._log('info', component, message, **kwargs)

    def warning(self, component, message, **kwargs):
        """Log warning message with component name"""
        self._log('warning', component, message, **kwargs)

    def error(self, component, message, **kwargs):
        """Log error message with component name"""
        self._log('error', component, message, **kwargs)

    def _log(self, level, component, message, **kwargs):
        """Internal method to log messages with consistent format"""
        log_message = f"[{component}] {message}"
        if kwargs:
            log_message += f" - Data: {json.dumps(kwargs)}"
        
        log_method = getattr(self.backend_logger, level)
        log_method(log_message)

# Create global logger instance
logger = ConfigHubLogger() 