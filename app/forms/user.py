from flask_wtf import FlaskForm as Form
from wtforms import validators, StringField, PasswordField
from wtforms.fields.html5 import EmailField

class LoginForm(Form):
    username = StringField('Username', [
        validators.Required(),
        validators.Length(min=4, max=25),])
    password = PasswordField('Password', [
        validators.Required(),
        validators.Length(min=4, max=25),])

class RegisterForm(Form):
    fullname = StringField('Full name', [
        validators.Required(),
        validators.Length(max=30),])
    email = EmailField('Email', [
        validators.Required(),
        validators.Length(max=50),])
    username = StringField('Username', [
        validators.Required(),
        validators.Length(min=4, max=25),
        validators.Regexp(
            r'^[\w.@+-]+$', 
            message="Allowed charaters are: Alphanumerics, '.', '@', '+', '-'"),])
    password = PasswordField('Password', [
        validators.Required(),
        validators.Length(min=4, max=25),
        validators.Regexp(r'^[\w.@+-]+$'),
        validators.EqualTo('confirm', message='Password must match'),])
    confirm = PasswordField('Repeat password')

class ValidationForm(Form):
    validation_code = StringField('Validation code',[
        validators.Required(),
        validators.Length(min=4, max=25),])

class LostForm(Form):
    email = EmailField('Email', [
        validators.Required(),
        validators.Length(max=50),])
