#!/usr/bin/env python

# Standard library
from random import choice
import string
import warnings

from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from flask import redirect, session, url_for, flash
from flask_admin.form import rules
from flask_admin.actions import action
from flask_admin.form.widgets import Select2Widget
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from jinja2 import Markup

# Import app
from app import app, admin, db
from app.models.user import User
from app.models.question import UnitCategory, Unit, Variable, \
        QuestionCategory, Question
from app.models.exercise import Exercise, Sheet
from app.common.tools import evaluate

def is_admin():
    """
    Check whether currently logged user is admin.

    Returns
    -------
    bool:
        True if user is logged and is admin, else False
    """
    is_admin = False
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            is_admin = user.is_admin
    return is_admin

def get_user():
    """
    Get currently logged user.

    Returns
    -------
    User: object
    """
    if 'username' in session:
        user = User.query.filter_by(username = session['username']).first()
        return user

class BaseView(ModelView):
    """
    Definition of basic view from which all others admin views will inherit. 
    This prevents non-admin users from messing up with the database and
    redirects them to the homepage.
    """
    def is_accessible(self):
        return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

class UserView(BaseView):
    """
    An admin view for User table.
    """
    column_list = ('fullname', 'email', 'username', 'enrolled', 'validated',
            'is_admin')
    column_searchable_list = ('username', 'email', 'fullname')
    column_labels = {
            'fullname': 'Full name',
            'email': 'Email',
            'username': 'Username',
            'password_tmp': '1-time Password',
            'random_seed': 'Random seed',
            'validation_code': 'Validation code',
            'enrolled': 'Enrolled',
            'validated': 'Validated',
            'is_admin': 'Admin'}
    form_rules = ('fullname', 'email', 'username', 
            'password_tmp', 'random_seed', 'validation_code', 
            'enrolled', 'validated', 'is_admin')

    @action("ban_user", "Ban user", "Ban selected users?")
    def ban_user(self, ids):
        """
        Ban users by generating a new validation code for them.
        """
        for id in ids:
            user = User.query.filter_by(id=id).first()
            user.validated = False
            need_new_valid = True
            while need_new_valid:
                alphanum = string.ascii_letters + string.digits
                new_valid = ''.join(choice(alphanum) for _ in range(6))
                if new_valid != user.validation_code:
                    user.validation_code = new_valid
                    need_new_valid = False
            try:
                db.session.commit()
            except:
                error = "Ban user can not be saved."
        flash(f"{len(ids)} users banned.")

    #def on_model_change(self, form, User):
    #    """
    #    ???
    #    """
    #    if not form.random_seed.data:
    #        User.random_seed = 42
    #        flash('set random seed to 42')
    #    if hasattr(form, 'password'):
    #        if form.password.data:
    #            User.password = form.password.data
    #        else:
    #            del form.password.data

class QuestionView(BaseView):
    """

    """

    def _question_formatter(view, context, model, name):
        if model.name:
            url = url_for('render', id=model.id)
            string = f"<a href={url}>{model.name}</a> (click to render)"
        else:
            string = ""
        return Markup(string)
    
    def create_form(self):
        return self._filtered(super(QuestionView, self).edit_form())

    def edit_form(self, obj):
        return self._filtered(super(QuestionView, self).edit_form(obj), 
                obj.id)

    def _filtered(self, form, id=None):
        self._query_id = id
        form.text_variables.query_factory = self._get_list
        form.correct_variable.query_factory = self._get_list
        form.wrong_variable.query_factory = self._get_list
        return form

    def _get_list(self):
        if self._query_id is not None:
            id = self._query_id
            question = self.session.query(Question).filter(
                    Question.id == id).first()
            _list = self.session.query(Variable).filter(
                    (Variable.question_id==id) | \
                    ((Variable.question==None) &\
                     (Variable.correct_question==None) &\
                     (Variable.wrong_question==None))).all()
            cv = question.correct_variable
            wv = question.wrong_variable
            if cv:
                _list.append(cv)
            if wv:
                _list.append(wv)
            return _list
        else:
            return self.session.query(Variable).filter(
                ((Variable.question==None) &\
                 (Variable.correct_question==None) &\
                 (Variable.wrong_question==None)))

    #def on_model_change(self, form, Question):
    #    """
    #    ???
    #    """
    #    msg = '"answer command" and "correct/wrong options" conflict'
    #    if form.answer_command.data:
    #        if form.correct_variable.data or form.wrong_variable.data:
    #            flash(msg)
    #            Question.correct_option = None
    #            Question.wrong_option = None
    #            Question.answer_command = None
    #    else:
    #        if not form.correct_variable.data or not form.wrong_variable.data:
    #            Question.no_answer = True

    column_list = ('name', 'body', 'no_answer')
    column_formatters = {'name': _question_formatter,}
    column_labels = {
            'name': 'Title',
            'body': 'Question text (mathjax)',
            'answer_command': 'answer command/text',
            'correct_variable': 'correct options',
            'wrong_variable': 'wrong options',
            'no_answer': 'no answer required',}
    column_searchable_list = ('name', 'body', 'no_answer')
    form_rules = ('category', 'name', 'body', 'answer_command', 
            'text_variables', 'answer_units', 'correct_variable', 
            'wrong_variable', 'no_answer')



class ExerciseView(BaseView):
    """

    """
    
    def _exercise_formatter(view, context, model, name):
        if model.name:
            url = url_for('exercise', id=model.id)
            string = f"<a href={url}>{model.name}</a> (click to render)"
        else:
            string = ""
        return Markup(string)

    column_formatters = {'name': _exercise_formatter}
    form_rules = ('questions', 'name', 'open_date', 'close_date', 'active')

class VariableView(BaseView):
    column_list = ('name', 'description', 'category')
    column_searchable_list = ('name', 'description', 'category')
    column_labels = {
            'name': 'Variable name',
            'description': 'Variable description',
            'constraint': 'Constraint: range-(), list-[]',
            'units': 'Allowed units',
            'correct_question': 'Used as correct options',
            'wrong_question': 'Used as wrong options'}
    form_choices = {
        'category': [ 
            ('int', 'Integer'), 
            ('float', 'Floating number'),
            ('str', 'String'),
            ('unit', 'Unit')]}
    form_widget_args = {
            'question':{'disabled':True},
            'correct_question':{'disabled':True},
            'wrong_question':{'disabled':True},}
    form_rules = ('category', 'name', 'description', 
            'constraint', 'units', 'question',
            'correct_question', 'wrong_question')

    #def on_model_change(self, form, Variable):
    #    print("Causes error")
    #    if '_' in form.name.data:
    #        flash('charactor "_" is reserved of operation, removing it')
    #        Variable.name = form.name.data.replace('_', '')

class SheetView(BaseView):
    """

    """
    def _point_formatter(view, context, model, name):
        if type(model.point) is float:
            url = url_for('reevaluate', id=model.id)
            string = f"<a href={url}>{model.point:4.2f}</a>"
            return Markup(string)

    column_formatters = {'point': _point_formatter}
    form_ajax_refs = {
            'user': {'fields': (User.fullname,)},
            'exercise': {'fields': (Exercise.name,)},
            'question': {'fields': (Question.name,)}}
    column_searchable_list = ('user.fullname', 'exercise.name', 'question.name')

    @action("reevaluate", "Reevaluate", "Reevaluate selected sheets?")
    def action_reevaluate(self, ids):
        for id in ids:
            sheet = Sheet.query.filter_by(id=id).first()
            evaluate(sheet.question, sheet, sheet.user.random_seed)
        flash(f"{len(ids)} sheets reevaluated")

    @action("deevaluate", "Deevaluate", "Deevaluate selected sheets (removing point)?")
    def action_deevaluate(self, ids):
        for id in ids:
            sheet = Sheet.query.filter_by(id=id).first()
            sheet.point = None
            try:
                db.session.commit()
            except:
                error = "Deevaluated sheet can not be saved."
        flash(f"{len(ids)} sheets deevaluated")

    @action("givepoint", "Give point", "Give point to selected sheets?")
    def action_givepoint(self, ids):
        for id in ids:
            sheet = Sheet.query.filter_by(id=id).first()
            sheet.point = 1.0
            try:
                db.session.commit()
            except:
                error = "Deevaluated sheet can not be saved."
        flash(f"{len(ids)} sheets deevaluated")


class UnitView(BaseView):
    column_list = ('name', 'fullname', 'face', 'SI_value', 'category.name')
    column_searchable_list = ('name', 'fullname', 'category.name')
    column_labels = {
            'name': 'Unit name',
            'face': 'LaTeX code',
            'SI_value': 'in SI unit'}
    form_rules = ('name', 'fullname', 'face', 'SI_value', 'category')

class UnitCategoryView(BaseView):
    column_list = ('name', 'm', 'kg', 's', 'A', 'K', 'mol', 'cd')
    column_labels = {
            'm': 'meter (m)',
            'kg': 'kilogram (kg)',
            's': 'second (s)',
            'A': 'ampere (A)',
            'K': 'kelvin (K)',
            'mol': 'mole (mol)',
            'cd': 'candela (cd)',}
    form_rules = ('name', 'm', 'kg', 's', 'A', 'K', 'mol', 'cd')

class HomeView(BaseView):
    """

    """

with warnings.catch_warnings():
    warnings.filterwarnings(
        'ignore', 'Fields missing from ruleset', UserWarning)
    print("Adding views")
    admin.add_view(UserView(User, db.session))
    admin.add_view(ExerciseView(Exercise, db.session))
    admin.add_view(QuestionView(Question, db.session))
    admin.add_view(BaseView(QuestionCategory, db.session))
    admin.add_view(VariableView(Variable, db.session))
    admin.add_view(SheetView(Sheet, db.session))
    admin.add_view(UnitView(Unit, db.session))
    admin.add_view(UnitCategoryView(UnitCategory, db.session))

#admin.add_view(UserView(User, db.session))

# Basic views
#admin.add_view(ModelView(User, db.session))
#admin.add_view(ModelView(Exercise, db.session))
#admin.add_view(ModelView(Question, db.session))
#admin.add_view(ModelView(QuestionCategory, db.session))
#admin.add_view(ModelView(Variable, db.session))
#admin.add_view(ModelView(Sheet, db.session))
#admin.add_view(ModelView(Unit, db.session))
#admin.add_view(ModelView(UnitCategory, db.session))


admin.add_link(MenuLink(name='Home', category='Links', url='/index'))
admin.add_link(MenuLink(name='Logout', category='Links', url='/logout'))
admin.add_link(MenuLink(name='Re-evaluate all', category='Links', url='/reevaluate'))
