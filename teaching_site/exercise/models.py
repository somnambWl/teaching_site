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

    def evaluate(self, seed):

        error = None
        point = 0.0
        status = 'text-danger'
        ans_msg = "You did not answer this question."
        print 'yo'
        print self
        print self.question
        print self.user
        if self.question:
            answer =  self.question.evaluate(seed)
            if type(answer) is float:
                if self.number:
                    tried = float(self.number)
                    if answer == 0 and abs(tried) < 1E-3:
                        point = 1.0
                        ans_msg = "Your answer is correct!"
                        status = 'text-success'
                    elif answer != 0\
                    and abs((tried - answer)/answer) < 0.1:
                        point = 1.0
                        ans_msg = "Your answer is correct!"
                        status = 'text-success'
                    else:
                        ans_msg = "The correct answer is %E," % answer\
                                  + " but you have entered %E." % tried
                else:
                    ans_msg = "You did not answer this question."
            else:
                answer = np.array(answer)
                mask = np.array([
                    self.option1,
                    self.option2,
                    self.option3,
                    self.option4,
                    self.option5,
                ])
                for m in range(len(mask)):
                    if mask[m] is None:
                        mask[m] = False

                n_options = len(self.question.render(seed)[1])
                choice = np.ma.masked_array(np.arange(1,6), ~mask)
                tried = np.array([c for c in choice[:n_options] if c])-1
                tried = tried.tolist()

                if not (self.option1 or self.option2 \
                or self.option3 or self.option4 or self.option5):
                    if not self.question.no_answer:
                        point = 0
                        ans_msg = "You did not answer this question."
                        status = "text-danger"
                else:
                    corrects = 0
                    for j in range(n_options):
                        if j in answer and j in tried:
                            corrects += 1
                            point += 1./n_options
                        elif j not in answer and j not in tried:
                            corrects += 1
                            point += 1./n_options
                        else:
                            point -= 1./n_options
                    if corrects == n_options:
                        ans_msg = "Your answer is correct!"
                        status = 'text-success'
                    else:
                        ans_msg = "The correct answer is options: %d" \
                                  % (answer[0] + 1)
                        for j in answer[1:]:
                            ans_msg += ", %d" % (j + 1)
                        ans_msg += ", but you chose options: %d" \
                                   % (tried[0] + 1)
                        for j in tried[1:]:
                            ans_msg += ", %d" % (j + 1)
                        ans_msg += '.'
                        status = 'text-warning'
                        if point <= 0:
                            status = 'text-danger'
                            ans_msg += " Negative points to "+\
                                "balence expectation value."
            ans_msg += " You've got %4.2f point." % (round(point, 3))

            self.point = point

            try:
                db.session.commit()
            except:
                error = "Evaluated results can not be saved, " +\
                        " please contact course administrator."
        return point, status, ans_msg, error
