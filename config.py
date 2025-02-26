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

class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')


class DevConfig(Config):
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True
    DATABASE_URI = environ.get('DEV_DATABASE_URI')
    SECRET_KEY = '1234'


    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", "sqlite:///softwareNews.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False