import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'dev-secret-key-apsa-2024'
    
    # En Vercel el sistema de archivos es de solo lectura excepto /tmp
    if os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_URL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/apsa.db'
        UPLOAD_FOLDER = '/tmp/qr_codes'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///apsa.db'
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'qr_codes')
        
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    APP_NAME = 'SSU - Seguro Social Universitario'
    APP_VERSION = '1.0.0'
    HOSPITAL_NAME = 'Seguro Universitario - UAGRM FINI'
    UNIVERSIDAD = 'UAGRM - Yapacaní'

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}