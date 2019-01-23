import os

# app setting
DEBUG = True
# database setting
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.dirname(__file__)}/app/data/app.db"

ROOT = 'admin'
MAIL_USERNAME = 'admin@gmail.com'   # Change here to get mail server working
MAIL_PASSWORD = 'some_password'     # Change here to get mail server working

SECRET_KEY = "TajnyKlic"

# Admin CSS theme
FLASK_ADMIN_SWATCH = 'sandstone' 
