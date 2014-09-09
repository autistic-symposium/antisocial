#!/usr/bin/env python

"""
	manage.py launches the application and other application tasks

	The script begins by creating an application.
	The configuration is from the configuration file.
"""


import os
from app import create_app, db
from app.models import User, Role, Permission, Post, Comment
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission,
                Post=Post, Comment=Comment)


# To create/upgrade the databases:
# $ python manage.py db upgrade
# To run as a shel:
# $ python manage.py shell
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



# The manager.command decorator makes it simple to implement custom commands.
# The name of the decorated function is used as the command name, and the
# function's docstring is displayed in the help message.
# to run tests:
# $ python manage.py test
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)




if __name__ == '__main__':
    manager.run()
