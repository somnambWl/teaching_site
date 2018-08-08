Flask teaching site framwork
============================

Python2.7

This is the exercise page for quantum chemistry. 
It is designed to automize the exercise evaluation using Flask/SQLAlchemy.

The following command should be executed before running the server
* pip install -r requirements.txt (assuming proper enviroment is setup)
* ./initialized.sh
* python manage.py runserver (debug mode)
* python manage.py gunicorn (production mode)

The admin is set to be 
* account: admin
* passwd: admin
(see teaching\_site/\_\_init.py\_\_)

__NOTE: PLEASE CHANGE THE EMAIL WITH CORRECT LOGIN__
It is necessary for sending email of validation code

The default admin address need to be changed to have gmail response for user password reset
