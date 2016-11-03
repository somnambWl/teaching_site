from teaching_site import db
from teaching_site.user.models import User
from teaching_site.question.models import Question
from datetime import datetime

question_exercise = db.Table(
    'question_exercise',
    db.Column(
        'exercise_id',
        db.Integer,
        db.ForeignKey('exercise.id')),
    db.Column(
        'question_id',
        db.Integer,
        db.ForeignKey('question.id')),
)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    open_date = db.Column(db.DateTime, nullable=False)
    close_date = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)
    questions = db.relationship(
        'Question',
        secondary = question_exercise,
        backref = db.backref('exercises', lazy='dynamic'),
    )

    def __repr__(self):
        return self.name

class Sheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Float)
    option1 = db.Column(db.Boolean, default=False)
    option2 = db.Column(db.Boolean, default=False)
    option3 = db.Column(db.Boolean, default=False)
    option4 = db.Column(db.Boolean, default=False)
    option5 = db.Column(db.Boolean, default=False)
    edit_date = db.Column(db.DateTime)
    point = db.Column(db.Float)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship(
        'User',
        backref=db.backref('sheets',lazy='dynamic')
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('exercise.id'),
        nullable=False)
    exercise = db.relationship(
        'Exercise',
        backref=db.backref('sheets',lazy='dynamic')
    )
    question_id = db.Column(
        db.Integer,
        db.ForeignKey('question.id'),
        nullable=False)
    question = db.relationship(
        'Question',
        backref=db.backref('sheets',lazy='dynamic')
    )

    def __repr__(self):
        try:
            return "%s %s %s" % (user.name, exercise.name, question.name)
        except:
            return "answer sheet"
