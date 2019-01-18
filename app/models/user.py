from app import db
from random import choice
import string
from numpy.random import randint

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(30))
    email = db.Column(db.String(50), unique = True)
    username = db.Column(db.String(25), unique = True)
    password = db.Column(db.String(100))
    password_tmp = db.Column(db.String(25))
    validation_code = db.Column(db.String(10))
    validated = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    random_seed = db.Column(db.Integer)

    def __init__(self, fullname='', email='', username='', 
                 password='', is_admin='', validated='',
                 validation_code = None, password_tmp = ''):
        self.fullname = fullname
        self.email = email
        self.username = username
        self.password = password
        self.password_tmp = password_tmp
        self.is_admin = is_admin
        self.random_seed = randint(1, 10000)
        if validation_code is None:
            alphanum = string.ascii_letters + string.digits
            self.validation_code = ''.join(choice(alphanum) \
                for _ in range(6))
        else:
            self.validation_code = validation_code
        if validated:
            self.validated = True
        else:
            self.validated = False

    def __repr__(self):
        return self.fullname
