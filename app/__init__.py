# app/__init__.py
# This is the main entry point for the Flask app
# I used the "app factory" pattern so that I can create
# multiple instances of the app for testing without them interfering

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# create the db object here so it can be imported by models.py
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """
    App factory function - creates and configures the Flask app.
    This pattern makes it easier to run tests with different configs.
    """
    app = Flask(__name__)

    # load config from environment variables, fallback to defaults for development
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///taskflow.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # suppress deprecation warning

    # initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints (groups of related routes)
    from app.routes import main
    app.register_blueprint(main)

    from app.api import api
    app.register_blueprint(api, url_prefix='/api')  # all API routes start with /api

    # create database tables if they don't exist yet
    with app.app_context():
        db.create_all()

    return app
