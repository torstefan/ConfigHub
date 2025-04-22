from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.config import bp as config_bp
    app.register_blueprint(config_bp, url_prefix='/config')

    from app.deploy import bp as deploy_bp
    app.register_blueprint(deploy_bp, url_prefix='/deploy')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    # Main application logger
    app_handler = RotatingFileHandler('logs/confighub.log',
                                    maxBytes=10240, backupCount=10)
    app_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app_handler.setLevel(logging.INFO)
    app.logger.addHandler(app_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('ConfigHub startup')

    # Frontend logger
    frontend_handler = RotatingFileHandler('logs/frontend.log',
                                         maxBytes=10240, backupCount=10)
    frontend_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    frontend_handler.setLevel(logging.INFO)
    frontend_logger = logging.getLogger('frontend')
    frontend_logger.addHandler(frontend_handler)
    frontend_logger.setLevel(logging.INFO)

    return app

from app import models 