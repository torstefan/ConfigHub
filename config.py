import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Git Configuration
    GIT_REPO_URL = os.environ.get('GIT_REPO_URL')
    GIT_TOKEN = os.environ.get('GIT_TOKEN')
    ROOT_FOLDER = os.environ.get('ROOT_FOLDER', '/opt/NetworkConfigGenerator')
    
    # Authentication Configuration
    AUTH_TYPE = os.environ.get('AUTH_TYPE', 'local')
    
    # LDAP Configuration
    LDAP_HOST = os.environ.get('LDAP_HOST')
    LDAP_PORT = int(os.environ.get('LDAP_PORT', 389))
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN')
    LDAP_USER_DN = os.environ.get('LDAP_USER_DN')
    LDAP_GROUP_DN = os.environ.get('LDAP_GROUP_DN')
    LDAP_USER_RDN_ATTR = os.environ.get('LDAP_USER_RDN_ATTR')
    LDAP_USER_LOGIN_ATTR = os.environ.get('LDAP_USER_LOGIN_ATTR')
    LDAP_GROUP_OBJECT_FILTER = os.environ.get('LDAP_GROUP_OBJECT_FILTER')
    LDAP_USER_OBJECT_FILTER = os.environ.get('LDAP_USER_OBJECT_FILTER')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/confighub.log') 