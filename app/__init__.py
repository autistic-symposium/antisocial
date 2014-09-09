"""
    In this application we are using "application factory", which
    makes the code much more organized and suitable for testing.
    So we move the creation of the application to this factory function
    that can be invoked from a script.
    This also give us the ability of creating multiple application instances.
"""

# The constructor imports most of the Flask extensions in use because
# there is no application instance to initialize them with
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()


# Flask-login initialization
login_manager = LoginManager()
# can be 'basic' or 'strong', strong keeps track of the client's IP address
# and browser agent, and log out if it detects a change
login_manager.session_protection = 'strong'
# sets the endpoint for the login page (the login route is inside a blueprint
# so it needs to be prefixed with the bluepring name)
login_manager.login_view = 'auth.login'


# Takes as argument the name of a configuration to use for the application.
# The configuration settings are defined in config.py.
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # init_app completes the initialization
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)



    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')


    return app
