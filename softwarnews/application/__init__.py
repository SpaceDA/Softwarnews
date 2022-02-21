from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from flask_login import LoginManager


# Globally accessible libraries
db = SQLAlchemy()
ckeditor = CKEditor()
bootstrap = Bootstrap()
login_manager = LoginManager()

def init_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object('config.DevConfig')
    db.init_app(app)



    login_manager.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)

    with app.app_context():
        # Include our Routes
        from . import routes
        from . import auth
        from softwarnews.admin import admin

        # Register Blueprints
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(routes.main_bp)
        app.register_blueprint(admin.admin_bp)


        # create database model
        db.create_all()

        return app

