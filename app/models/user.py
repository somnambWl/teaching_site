#!/usr/bin/env python

from random import choice
import string
from numpy.random import randint

from app import db

class User(db.Model):
    """
    Definition of table for users.

    The information we store about each user are their ID, their full name,
    email, username, password, temporary password, validation code, if they 
    are validated already, if they are admin and their random seed.

    User can log in using both password and temporary password, however
    temporary password is usually set to '' and this is unacceptable as
    password. When they forget their password, temporary password can be set
    and after its first use it is set to '' again and users are asked to set a
    new password. 

    Validation code is used only once, afterwards validated is set to True.

    Random seed is stored in the database too, because we want to use the same
    seed for the same user everytime. This way, all students will have
    different questions randomized using their personal random seed.
    """
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

    def __init__(self, fullname='', email='', username='', password='', 
            is_admin='', validated='', validation_code = None, 
            password_tmp = ''):
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
