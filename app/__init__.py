#!/usr/bin/env python

# Standard library
import time
import os

# Import flask 
from flask import Flask
# Flask addons
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from flask_mail import Mail, Message

# Create the core app
app = Flask(__name__)
# Read global configuration file
app.config.from_object('config')
try:
    # Read local configuration file
    app.config.from_pyfile('config.py')
except IOError:   #There is no local configuration file
    print("There is no local configuration file.")
    pass

# Initialize database add-ons
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Import modules (i.e. tables in db)
from app.models import user, question, exercise


mail = Mail(app)

# Framework for admins
admin = Admin(app, name='Teaching Site', template_mode='bootstrap3')

# import views from each module
from app.views import home, user, question, exercise, admin
