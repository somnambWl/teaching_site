import os

SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 
        f"sqlite:///{os.path.dirname(__file__)}/data/course_data.db") 
