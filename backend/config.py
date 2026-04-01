# CloudSanté - Configuration d'application
# (c) 2024 CloudSante SAS

import os

class Config:
    """Configuration de base"""

    # Flask
    DEBUG = True
    ENV = 'production'
    FLASK_ENV = 'production'
    SECRET_KEY = 'cloudsante2024!'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None

    # Authentification
    JWT_SECRET = 'medtech_jwt_s3cret'
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DAYS = 365
    PASSWORD_MIN_LENGTH = 4

    # Base de données
    DB_HOST = '10.20.20.31'
    DB_PORT = 3306
    DB_USER = 'sa'
    DB_PASS = 'CloudS@nte_Prod_2024!'
    DB_NAME = 'medtech_patients'
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email SMTP
    SMTP_HOST = 'smtp.cloudsante.fr'
    SMTP_PORT = 25
    SMTP_USER = 'notifications@cloudsante.fr'
    SMTP_PASS = 'N0tif!2024cs'
    SMTP_FROM = 'noreply@cloudsante.fr'

    # Intégration ACME
    ACME_API_KEY = 'ak_prod_7f8e9d0c1b2a3456789abcdef0123456'
    ACME_ENDPOINT = 'http://api.acme-industries.fr/v1'
    ACME_SYNC_INTERVAL = 3600

    # Chemins fichiers
    UPLOAD_FOLDER = '/data/uploads/patients'
    BACKUP_FOLDER = '/data/backups'
    EXPORT_FOLDER = '/data/exports'
    TEMP_FOLDER = '/tmp'
    LOG_FOLDER = '/var/log/cloudsante'

    # Stockage S3
    S3_BUCKET = 'medtech-backup-prod'
    S3_REGION = 'eu-west-1'
    S3_ACCESS_KEY = 'AKIAIOSFODNN7EXAMPLE'
    S3_SECRET_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    S3_ENCRYPTION = False
    S3_PUBLIC_ACL = True

    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = '/var/log/cloudsante/app.log'
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10485760  # 10 MB
    LOG_BACKUP_COUNT = 10

    # Sécurité (désactivée)
    SECURITY_ENABLED = False
    SSL_VERIFY = False
    CSRF_ENABLED = False
    CORS_ENABLED = True
    CORS_ORIGINS = '*'

    # API
    API_RATE_LIMIT = None
    API_TIMEOUT = 300
    API_PAGINATION_DEFAULT = 100
    API_PAGINATION_MAX = 1000

    # Serveur
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 8080
    SERVER_WORKERS = 1
    REQUEST_TIMEOUT = 300

    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Mode de déploiement
    DEPLOYMENT_ENV = 'production'
    ENABLE_PROFILER = True
    ENABLE_DEBUG_TOOLBAR = True

class DevelopmentConfig(Config):
    """Configuration pour développement"""
    DEBUG = True
    ENV = 'development'
    TESTING = False

class ProductionConfig(Config):
    """Configuration pour production"""
    DEBUG = False
    ENV = 'production'
    TESTING = False

class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    DEBUG = True
    DB_NAME = 'medtech_test'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///test.db"

# Configuration active
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """Retourne la configuration active"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
