Flask teaching site framwork
============================

This is the exercise page for quantum chemistry. 
It is designed to automize the exercise evaluation using Flask/SQLAlchemy.

The following command should be executed before running the server
* pip install -r requirements.txt (assuming proper enviroment is setup)
* ./initialized.sh
* python manage.py runserver (debug mode)
* python manage.py gunicorn (production mode)

The admin is set to be 
* account: admin@gmail.com
* passwd: admin
(see teaching\_site/\_\_init.py\_\_)

The default admin address need to be changed to have gmail response for user password reset
