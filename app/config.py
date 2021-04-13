from os import environ


class Config:
    """Set Flask configuration from .env file."""

    # General Config
    FLASK_ENV = environ.get("FLASK_ENV")

    # Flask-Caching related configs
    CACHE_TYPE = environ.get("CACHE_TYPE")
    CACHE_REDIS_URL = environ.get("CACHE_REDIS_URL")
    CACHE_DEFAULT_TIMEOUT = int(environ.get("CACHE_DEFAULT_TIMEOUT", 300))

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Data
    DATA_DIR = environ.get("DATA_DIR")
