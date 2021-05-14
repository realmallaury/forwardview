import os
import secrets
from os import path

from dotenv import load_dotenv
from flask import Flask
from flask_assets import Environment
from flask_caching import Cache
from flask_login import LoginManager
from flask_cachebuster import CacheBuster
from pymysql import install_as_MySQLdb

from app.config import Config
from app.db import db
from app.db.models import User

cache = Cache()


def create_app():
    base_path = os.path.abspath(os.getcwd())
    resources_path = base_path + "/resources/"

    app = Flask(
        __name__,
        template_folder=resources_path + "templates",
        static_folder=resources_path + "static",
        instance_relative_config=False,
    )

    load_dotenv(path.join(base_path, ".env"))
    app.config.from_object(Config)

    assets = Environment()
    assets.init_app(app)

    install_as_MySQLdb()
    db.init_app(app)
    try:
        db.create_all(app=app)
    except:
        pass

    cache.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from app.endpoint.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from app.endpoint.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    # blueprint for ticker parts of app
    from app.endpoint.ticker import ticker as ticker_blueprint

    app.register_blueprint(ticker_blueprint)

    return app
