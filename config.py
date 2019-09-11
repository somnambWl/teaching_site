import os

# app setting
DEBUG = True
# database setting
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.dirname(__file__)}/app/data/app.db"

ROOT = 'admin'
MAIL_USERNAME = 'user@somewhere.something'   # Change here to get mail server working
MAIL_PASSWORD = 'MailPassword'     # Change here to get mail server working
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

SECRET_KEY = "TajnyKlic"

# Admin CSS theme
FLASK_ADMIN_SWATCH = 'sandstone' 
