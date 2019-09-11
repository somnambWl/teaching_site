
from random import choice
import string
from numpy.random import randint
from datetime import datetime

from flask import render_template, redirect, url_for, flash, session, \
        abort, request
import bcrypt

from app import app, db
from app.forms.user import RegisterForm, LoginForm, ValidationForm, LostForm
from app.models.user import User
from app.common.decorators import login_required, only_from
from app.common.mail import send_email

def login_user(user):
    session['username'] = user.username
    session['is_admin'] = user.is_admin

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if request.method=='GET' and request.args.get('next'):
        session['next'] = request.args.get('next', None)
    if form.validate_on_submit():   # After submission of login formular
        # Search for user with submitted username
        user = User.query.filter_by(username=form.username.data).first()
        if user:   # If the user does exist
            if user.password != '':   # Check if password was submitted
                try:
                    # Encrypt password
                    # (In the database there are only hashed passwords,
                    #  so we need to encrypt it everytime the same way)
                    password_in = bcrypt.hashpw(
                            form.password.data.encode("utf8"), 
                            user.password)
                except TypeError:
                    password_in = ''
            else:
                password_in = form.password.data.encode("utf8")
            # If the password hash matches the one in the database or the
            # temporary one:
            if password_in == user.password \
                    or form.password.data == user.password_tmp:
                # set session variable username when login
                msg = f"{datetime.now().strftime('%Y/%m/%d-%H:%M:%S')}: " \
                        f"{user.username} logged in from {request.remote_addr}."
                app.logger.info(msg)
                msg = f"{user.username}-agent: {getattr(request, 'user_agent')}"
                app.logger.info(msg)
                login_user(user)
                # If the temporary password was used:
                if form.password.data == user.password_tmp:
                    # Reset the temporary password
                    user.password_tmp = ''
                    db.session.commit()
                    flash('Temporary password expired.')
                    flash('Please, reset your password.')
                    # Redirect to the profile page
                    return redirect(url_for('user_setting'))
                # If the user is not validated, redirect him for validation
                if not user.validated:
                    return redirect(url_for('validate'))
                if 'next' in session:
                    next = session.get('next')
                    session.pop('next')
                    return redirect(next)
                else:
                    flash(f"Login as {session['username']}")
                    return redirect(url_for('index'))
            else:
                error = "Incorrect username or password"
        else:
            error = "Incorrect username or password"
    return render_template('user/login.html', form=form, error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    error = ""
    if form.validate_on_submit():
        # Convert password to hashed password
        salt = bcrypt.gensalt()
        hashedpw = bcrypt.hashpw(form.password.data.encode("utf8"), salt)
        #OldTODO check register list
        #OldTODO check admin
        #OldTODO get random seed
        # Load data from formular to User class
        is_admin = False
        validated = False
        user_new = User(form.fullname.data, form.email.data, 
                form.username.data, hashedpw, is_admin, validated)
        # Check for already registered user with same email
        user_old = User.query.filter_by(email=form.email.data).first()
        if user_old:   # Email address already used
            if user_old.validated:
                error = f"E-mail address {user_new.email} already registered"
                return render_template('user/register.html', 
                        form=form, error=error)
            else:
                user_old.fullname = user_new.fullname
                user_old.username = user_new.username
                user_old.password = hashedpw
                session['username'] = user_new.username
                session['is_admin'] = user_new.is_admin
                db.session.commit()
                send_validation_email()
                return redirect(url_for('validate'))
        # Email address was not used, so add new user to the database
        try:
            db.session.add(user_new)
            db.session.flush()
        except:   # Username was taken, so try registration once again
            error = f"Username {user_new.username} is already taken."
            return render_template('user/register.html', 
                    form=form, error=error)
        # Nor email address nor username were used, finalize saving to the
        # database, login user and send him a validation email.
        if user_new.id:
            db.session.commit()
            flash(f"User {form.username.data} created")
            session['username'] = form.username.data
            session['is_admin'] = is_admin
            send_validation_email()
            return redirect(url_for('validate'))
        else:
            db.session.rollback()
            error = "Error creating user, please try again or contact administrator."
    return render_template('user/register.html', form=form, error=error)

@app.route('/validate', methods=['GET', 'POST'])
@login_required
def validate():
    form = ValidationForm()
    error = ""
    user = User.query.filter_by(
            username=session['username'],).first()
    user_id = user.id
    if user.validated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        validate_input = form.validation_code.data
        if validate_input == user.validation_code:
            user.validated = True
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('user/validate.html', form=form, user=user, 
            user_id=user_id, error = error)
    
@app.route('/send_validate_email')
@login_required
@only_from('validate', 'register')
def send_validation_email():
    user = User.query.filter_by(username=session['username']).first()
    title = "Validation code"
    text_list = [
            f"Welcome {user.fullname} \n\n",
            f"Your validation code is: {user.validation_code} \n"]
    body = ''.join(text_list)
    send_email(user.email, title, body)
    flash(f'Sending validation email to {user.email}')
    return redirect(url_for('validate'))

@app.route('/lost_password', methods=['GET', 'POST'])
@only_from('login', 'lost_password')
def lost_password():
    form = LostForm()
    error = ""
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        msg = f"{datetime.now().strftime('%Y/%m/%d-%H:%M:%S')}: request for" \
                f" lost password reset for email: {user.email}" \
                f", from IP: {request.remote_addr}"
        app.logger.warning(msg)
        if user:
            if user.validated:
                alphanum = string.ascii_letters + string.digits
                password_new = ''.join(choice(alphanum) \
                    for _ in range(8))
                user.password_tmp = password_new
                db.session.commit()
                title = 'Reset password'
                body = f"Hi {user.fullname}, \n\n" \
                        f"Your temporary password is: {password_new}\n"
                send_email(user.email, title, body)
            flash('Inscruction has been sent')
        #flash('No email found')
    return render_template('user/lost.html', form=form)

@app.route('/logout')
@login_required
def logout():
    username = session['username']
    session.pop('username')
    if 'is_admin' in session:
        session.pop('is_admin')
    flash(f'Logged out from user: {username}')
    return redirect(url_for('index'))

@app.route('/user_setting', methods=['GET', 'POST'])
@login_required
def user_setting():
    user = User.query.filter_by(username = session['username']).first()
    if user.validated:
        form = RegisterForm(obj=user)
        error = ''
        if form.validate_on_submit():
            salt = bcrypt.gensalt()
            hashedpw = bcrypt.hashpw(form.password.data.encode("utf8"), salt)
            if user.username != form.username.data:
                user.username = form.username.data
                session['username'] = user.username
                flash(f'Logged in as {user.username}')
            user.fullname = form.fullname.data
            user.password = hashedpw
            try:
                db.session.commit()
                flash('User data updated')
                msg = f"{datetime.now().strftime('%Y/%m/%d-%H:%M:%S')}:"\
                        f" user update for email: {user.email}" \
                        f", new username: {user.username}"
                app.logger.warning(msg)
            except:
                error = f'New username {form.username.data} is already taken.'
        return render_template('user/user_setting.html', 
                form=form, error=error, user=user)
    else:
        return redirect(url_for('validate'))
