from teaching_site import app, admin, db
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from teaching_site.user.models import User
from teaching_site.question.models import UnitCategory, Unit
from teaching_site.question.models import Variable
from teaching_site.question.models import QuestionCategory, Question
from teaching_site.exercise.models import Exercise, Sheet
from flask import redirect, session, url_for, flash
from flask_admin.form import rules
import warnings
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from flask_admin.form.widgets import Select2Widget
from jinja2 import Markup

def is_admin():
    is_admin = False
    if 'username' in session:
        user = User.query.filter_by(
            username = session['username']
        ).first()
        if user:
            is_admin = user.is_admin
    return is_admin

def get_user():
    if 'username' in session:
        user = User.query.filter_by(
            username = session['username']
        ).first()
        return user

class BaseView(ModelView):
    def is_accessible(self):
        return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

class UserView(BaseView):
    column_list = ('fullname', 'email', 
        'username', 'validated', 'is_admin')
    column_searchable_list = ('username', 'email', 'fullname')
    column_labels = {
        'fullname': 'Full name',
        'email': 'Email',
        'username': 'Username',
        'password_tmp': '1-time Password',
        'random_seed': 'Random seed',
        'validated': 'Validated',
        'is_admin': 'Admin',
    }
    form_rules = ('fullname', 'email', 'username', 
        'password_tmp', 'random_seed', 'validated', 'is_admin')

    def on_model_change(self, form, User):
        if not form.random_seed.data:
            User.random_seed = 42
            flash('set random seed to 42')
        if hasattr(form, 'password'):
            if form.password.data:
                User.password = form.password.data
            else:
                del form.password.data


class QuestionView(BaseView):
    def _question_formatter(view, context, model, name):
        return Markup(
            "<a href='%s'>%s</a> (%s)" % (
                url_for('render', id=model.id),
                model.name,
                'click to render'
            ) if model.name else ""
        )

    column_list = (
        'name', 'body', 'no_answer'
    )

    column_formatters = {
        'name': _question_formatter,
    }

    column_labels = {
        'name': 'Title',
        'body': 'Question text (mathjax)',
        'answer_command': 'answer command/text',
        'correct_variable': 'correct options',
        'wrong_variable': 'wrong options',
        'no_answer': 'no answer required',
    }
    column_searchable_list = (
        'name', 'body', 'no_answer'
    )
    form_rules = ('category', 'name', 'body', 'answer_command', 
        'text_variables', 'answer_units', 'correct_variable', 
        'wrong_variable', 'no_answer')

    def create_form(self):
        return self._filtered(
            super(QuestionView, self).edit_form(),
        )

    def edit_form(self, obj):
        return self._filtered(
            super(QuestionView, self).edit_form(obj), obj.id
        )

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
                Question.id == id
            ).first()
            _list = self.session.query(Variable).filter(
                (Variable.question_id==id) | \
                ((Variable.question==None) &\
                 (Variable.correct_question==None) &\
                 (Variable.wrong_question==None))
            ).all()
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

    def on_model_change(self, form, Question):
        msg = '"answer command" and "correct/wrong options" conflict'
        if form.answer_command.data:
            if form.correct_variable.data\
            or form.wrong_variable.data:
                flash(msg)
                Question.correct_option = None
                Question.wrong_option = None
                Question.answer_command = None
        else:
            if not form.correct_variable.data\
            or not form.wrong_variable.data:
                Question.no_answer = True

class ExerciseView(BaseView):
    def _exercise_formatter(view, context, model, name):
        return Markup(
            "<a href='%s'>%s</a> (%s)" % (
                url_for('exercise', id=model.id),
                model.name,
                'click to render'
            ) if model.name else ""
        )
    column_formatters = {
        'name': _exercise_formatter,
    }
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
        'wrong_question': 'Used as wrong options',
    }
    form_choices = {
        'category': [ 
            ('int', 'Integer'), 
            ('float', 'Floating number'),
            ('str', 'String'),
            ('unit', 'Unit'),
        ],
    }
    form_widget_args = {
        'question':{
            'disabled':True
        },
        'correct_question':{
            'disabled':True
        },
        'wrong_question':{
            'disabled':True
        },
    }
    form_rules = ('category', 'name', 'description', 
        'constraint', 'units', 'question',
        'correct_question', 'wrong_question')

    def on_model_change(self, form, Variable):
        if '_' in form.name.data:
            flash('charactor "_" is reserved of operation, removing it')
            Variable.name = form.name.data.replace('_', '')

class SheetView(BaseView):
    form_ajax_refs = {
        'user': {
            'fields': (User.fullname,),
        },
        'exercise': {
            'fields': (Exercise.name,),
        },
        'question': {
            'fields': (Question.name,),
        },
    }
    column_searchable_list = ('user.fullname', 'exercise.name', 'question.name')

class UnitView(BaseView):
    column_list = ('name', 'fullname', 'face', 'SI_value', 'category.name')
    column_searchable_list = ('name', 'fullname', 'category.name')
    column_labels = {
        'name': 'Unit name',
        'face': 'LaTeX code',
        'SI_value': 'in SI unit',
    }
    form_rules = ('name', 'fullname', 'face', 
        'SI_value', 'category')

class UnitCategoryView(BaseView):
    column_list = ('name',)
    column_labels = {
        'm': 'meter (m)',
        'kg': 'kilogram (kg)',
        's': 'second (s)',
        'A': 'ampere (A)',
        'K': 'kelvin (K)',
        'mol': 'mole (mol)',
        'cd': 'candela (cd)',
    }
    form_rules = ('name', 'm', 'kg', 's', 'A', 'K', 'mol', 'cd')

with warnings.catch_warnings():
    warnings.filterwarnings(
        'ignore', 'Fields missing from ruleset', UserWarning)
    admin.add_view(UserView(User, db.session))
    admin.add_view(ExerciseView(Exercise, db.session))
    admin.add_view(QuestionView(Question, db.session))
    admin.add_view(BaseView(QuestionCategory, db.session))
    admin.add_view(VariableView(Variable, db.session))
    admin.add_view(SheetView(Sheet, db.session))
    admin.add_view(UnitView(Unit, db.session))
    admin.add_view(UnitCategoryView(UnitCategory, db.session))
admin.add_link(MenuLink(name='Home', category='Links', url='/index'))
admin.add_link(MenuLink(name='Logout', category='Links', url='/logout'))
