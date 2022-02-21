from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Base Config"""
    FLASK_APP = 'wsgi.py'
    SECRET_KEY = environ.get("SECRET_KEY")
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(Config):
    """Production Config - Change on __init__.py"""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = environ.get('DATABASE_URL')

class DevConfig(Config):
    """Development Config - Change on __init__.py"""
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True
    DATABASE_URI = environ.get('DEV_DATABASE_URI')

