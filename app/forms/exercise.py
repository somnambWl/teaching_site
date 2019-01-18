from flask_wtf import FlaskForm as Form
from wtforms.fields import BooleanField
from wtforms import validators, FloatField

class QuestionForm(Form):
    number = FloatField('Answer')
    option1 = BooleanField('Option1')
    option2 = BooleanField('Option2')
    option3 = BooleanField('Option3')
    option4 = BooleanField('Option4')
    option5 = BooleanField('Option5')
