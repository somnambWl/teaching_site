
from datetime import datetime

from app import db
from app.models.user import User
from app.models.question import Question

# Many-to-many lookup tables

question_exercise = db.Table('question_exercise',
        db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id')),
        db.Column('question_id', db.Integer, db.ForeignKey('question.id')),)

# Normal tables

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    open_date = db.Column(db.DateTime, nullable=False)
    close_date = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)
    questions = db.relationship('Question', secondary=question_exercise,
            backref=db.backref('exercises', lazy='dynamic'))

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

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', 
            backref=db.backref('sheets',lazy='dynamic'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'),
            nullable=False)
    exercise = db.relationship('Exercise',
            backref=db.backref('sheets',lazy='dynamic'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'),
            nullable=False)
    question = db.relationship('Question', 
            backref=db.backref('sheets',lazy='dynamic'))

    def __repr__(self):
        try:
            return f"{user.name} {exercise.name} {question.name}"
        except:
            return "answer sheet"
