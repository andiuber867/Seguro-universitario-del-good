import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'dev-secret-key-apsa-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///apsa.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'qr_codes')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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