from flask import Flask, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskext.markdown import Markdown
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_mail import Mail, Message
from flask_admin import Admin, AdminIndexView
import logging
from logging.handlers import RotatingFileHandler
from time import sleep
import os

# treat every thing as a package!
app = Flask(__name__)
# modulize config from setting file
app.config.from_pyfile('config/settings.py')
base_setting = {
    'ROOT': 'user@gmail.com',
    'MAIL_USERNAME': 'user@gmail.com',
    'MAIL_PASSWORD': 'some_password',
    'SECRET_KEY': 'some key',
}
for key, value in base_setting.items():
    if key not in os.environ or os.environ[key] is None:
        app.config[key] = value
    else:
        app.config[key] = os.environ[key]

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///%s/data/course_data.db' % os.path.dirname(__file__))

# database
db = SQLAlchemy(app)

# migrate
migrate = Migrate(app, db)

# Markdown
Markdown(app)

# logger
handler = RotatingFileHandler(
    'security.log', 
    maxBytes=10000, 
    backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# admin
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return False
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))
admin = Admin(app, index_view=MyAdminIndexView())

# mail
mail = Mail(app)
def send_email(recipients, title, body):
    sleep(0.5)
    if type(recipients) is not list:
        recipients = [recipients]
    msg = Message(
        title,
        sender=os.getenv('MAIL_USERNAME', 'user@gmail.com'),
        recipients = recipients
    )
    msg.body = body
    mail.send(msg)

# images
uploaded_images = UploadSet('images', IMAGES)
configure_uploads(app, uploaded_images)

# import views from each module
from teaching_site.exercise import views
from teaching_site.user import views
from teaching_site.question import views
from teaching_site.admin_views import views
from teaching_site.home import views
