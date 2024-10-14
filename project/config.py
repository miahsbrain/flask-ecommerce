import sys
import os

packages = [p for p in sys.path if 'site-packages' in p][-1]
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(packages, 'project.pth'), 'w') as f:
    f.write(basedir)

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'local_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Set to False in production
    

class DevelopmentConfig(Config):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

class TestingConfig(Config):
    """Testing configuration."""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    TESTING = True

class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Get from environment variable
    DEBUG = False

config = dict(development=DevelopmentConfig, test=TestingConfig, production=ProductionConfig)