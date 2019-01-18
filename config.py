import os

# app setting
DEBUG = True
# database setting
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.dirname(__file__)}/app/data/app.db"

SECRET_KEY = "TajnyKlic"

# Admin CSS theme
FLASK_ADMIN_SWATCH = 'sandstone' 
