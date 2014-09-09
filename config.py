__author__="Marina Wahl"


"""
	The config file stores the configuration settings
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))



"""
	The Config base class contains settings that are common to all configurations.
"""
class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ANTISOCIAL_MAIL_SUBJECT_PREFIX = '[The Anti-Social Network]'
    ANTISOCIAL_MAIL_SENDER = 'The Anti-Social Network Admin <thesuperantisocialnetwork@gmail.com>'
    ANTISOCIAL_ADMIN = os.environ.get('ANTISOCIAL_ADMIN')
    ANTISOCIAL_POSTS_PER_PAGE = 20
    ANTISOCIAL_FOLLOWERS_PER_PAGE = 20
    ANTISOCIAL_COMMENTS_PER_PAGE = 10

    #  takes an application instance as as argument
    @staticmethod
    def init_app(app):
        pass



"""
	The additional config classes define settings that are specific to a configuration.
	For instance, SQLALCHEMY_DATABASE_URI is assigned different values under each of the configurations (different databases for each situation).
"""
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
