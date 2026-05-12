# app/__init__.py
# this is where the flask app gets created
# i used the "app factory" pattern which basically means
# instead of creating the app directly, i wrap it in a function
# that way i can create separate versions for testing without them messing each other up

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# i create db here (outside the function) so that models.py can import it
# if i put it inside create_app(), other files wouldn't be able to reach it
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    app = Flask(__name__)

    # load settings from environment variables
    # if the variable isn't set, fall back to a default (useful for local dev)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///taskflow.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # turns off an annoying warning

    # connect the db and migrate objects to this app
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints - these are just groups of related routes
    # i split them into two files to keep things organized
    from app.routes import main
    app.register_blueprint(main)

    from app.api import api
    app.register_blueprint(api, url_prefix='/api')  # all api routes will start with /api/...

    # create the database tables if they don't exist yet
    # needs app_context() because flask needs to know which app we're talking about
    with app.app_context():
        db.create_all()

    return app
