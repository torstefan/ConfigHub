from flask import request, jsonify
from app.api import bp
import logging

frontend_logger = logging.getLogger('frontend')

@bp.route('/log', methods=['POST'])
def log_frontend():
    """Endpoint to receive and log frontend messages"""
    data = request.get_json()
    
    if not data or 'level' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid log data'}), 400
        
    level = data.get('level', 'info').lower()
    message = data.get('message', '')
    
    # Map frontend log levels to Python logging levels
    level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    log_level = level_map.get(level, logging.INFO)
    frontend_logger.log(log_level, message)
    
    return jsonify({'status': 'success'}) 