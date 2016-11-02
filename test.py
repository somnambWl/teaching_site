import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import bcrypt
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

from teaching_site import app, db

from teaching_site.user.models import *
from teaching_site.question.models import *
#from post.models import *

class UserTest(unittest.TestCase):
    def setUp(self):
        self.db_uri = 'sqlite:///%s/teaching_site/data/test_data.db' % os.path.dirname(__file__)
        app.config['TESTING'] = True
        # CSRF do not respond to script input, i.e. hidden_tag
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
        db.session.commit()
        db.create_all()

        password = bcrypt.hashpw('test', bcrypt.gensalt()) 

        test_notvalid = User(
            fullname = 'test not valid', 
            email='test@email', 
            username='validate', 
            password = password,
            validation_code = '123456',
            is_admin=False, 
            validated=False)

        test_user = User(
            fullname = 'test user', 
            email='user@email', 
            username='user', 
            password = password,
            password_tmp = 'test_tmp',
            is_admin=False, 
            validated=True)

        test_admin = User(
            fullname = 'test admin', 
            email='admin@email', 
            username='admin', 
            password = password,
            is_admin=True, 
            validated=True)

        db.session.add(test_notvalid)
        db.session.add(test_user)
        db.session.add(test_admin)
        db.session.commit()

        self.app = app.test_client()

    def tearDown(self):
        db.session.commit()
        db.drop_all()
        db.session.remove()

    def login(self, user, passwd):
        return self.app.post('/login', data=dict(
            username = user,
            password = passwd,
        ), follow_redirects = True)

    def test_normal_login(self):
        rv = self.login('user', 'test')
        assert 'login as user' in str(rv.data)
        assert 'Home' in str(rv.data)

    def test_notvalidated_login(self):
        rv = self.login('validate', 'test')
        assert 'Loged in as validate' in str(rv.data)
        assert 'User Data' in str(rv.data)
    
    def test_admin_login(self):
        rv = self.login('admin', 'test')
        assert 'Loged in as admin' in str(rv.data)
        assert 'Admin' in str(rv.data)

    def test_password_tmp(self):
        rv = self.login('user', 'test_tmp')
        assert 'temporary password expired' in str(rv.data)
        assert 'Loged in as user' in str(rv.data)
        assert 'Repeat password' in str(rv.data)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(UserTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
