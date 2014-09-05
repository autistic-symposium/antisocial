"""
	Defines the UNIT TESTS
"""


import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):

    # run before each test
    # try to create an enviroment for the test that is 
    # close to that of the running application
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # run after tests	
    # remove the database and the application context
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
