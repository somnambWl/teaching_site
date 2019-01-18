#!/usr/bin/env python

# Import flask 
from flask import Flask
# Flask addons
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

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

db = SQLAlchemy(app)
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='Teaching Site', template_mode='bootstrap3')

# import views from each module
#from app.views import home, user, question, exercise, admin_views
from app.views import home
