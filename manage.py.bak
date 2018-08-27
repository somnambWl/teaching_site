import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'teaching_site')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
#from flask.ext.script import Manager, Server
from flask_script import Manager, Server, Command, Option
from flask_migrate import MigrateCommand
from teaching_site import app, db
from teaching_site.user.models import User
from teaching_site.question.models import UnitCategory, Unit
from teaching_site.question.models import Variable, Question
from teaching_site.question.models import QuestionCategory
from teaching_site.exercise.models import Exercise
from datetime import datetime
from dateutil.relativedelta import relativedelta

class GunicornServer(Command):
    description = 'Run the app within Gunicorn'
    #def __init__(self, host='0.0.0.0', port=int(os.getenv('PORT', 8000)), workers=4):
    def __init__(self, host='127.0.0.1', port=80, workers=4):
        self.port = port
        self.host = host
        self.workers = workers

    def get_options(self):
        return (
            Option('-H', '--host',
                   dest='host',
                   default=self.host),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port),
            Option('-w', '--workers',
                   dest='workers',
                   type=int,
                   default=self.workers),
        )

    def __call__(self, app, host, port, workers):
        from gunicorn import version_info
        if version_info < (0, 9, 0):
            from gunicorn.arbiter import Arbiter
            from gunicorn.config import Config
            arbiter = Arbiter(Config({'bind': "%s:%d" % (host, int(port)),'workers': workers}), app)
            arbiter.run()
        else:
            from gunicorn.app.base import Application
            class FlaskApplication(Application):
                def init(self, parser, opts, args):
                    return {
                        'bind': '{0}:{1}'.format(host, port),
                        'workers': workers 
                    }

                def load(self):
                    return app
            FlaskApplication().run()

manager = Manager(app)

manager.add_command(
    'db', 
    MigrateCommand
)

manager.add_command(
    "runserver",
    Server(
        use_debugger = True,
        use_reloader = True,
        host = os.getenv('IP', '0.0.0.0'),
        port = int(os.getenv('PORT', 5000))
    ) 
)

manager.add_command(
    "gunicorn", GunicornServer()
)

@manager.command
def init():
    db.create_all()
    email = app.config['ROOT']
    admin = User(
        username = email,
        email = email,
        password_tmp = 'admin',
        validated = True,
        is_admin = True
    )
    db.session.add(admin)
    try:
        db.session.commit()
    except:
        print "admin can not be added"

@manager.command
def create_unit():
    for name, base in app.config['UNIT_CATAGORIES'].items():
        unit = UnitCategory(name, *base)
        db.session.add(unit)
    try:
        db.session.commit()
    except:
        pass
    for unit_config in app.config['UNITS']:
        db.session.add(Unit(*unit_config))
        try:
            db.session.commit()
        except:
            print unit[0],
            print 'failed'

@manager.command
def create_variable():
    for variable in app.config['VARIABLES']:
        if 'units' in variable:
            unit_list = variable.pop('units')
            units = []
            for unit_str in unit_list:
                unit = Unit.query.filter_by(
                    name = unit_str
                ).first()
                if unit is not None:
                    units.append(unit)
                else:
                    print "%s not found" % unit_str
            variable['units'] = units
        db.session.add(Variable(
            **variable
        ))
    db.session.commit()

@manager.command
def create_question():
    obj_list_dict = {
        'text_variables': Variable,
        'answer_units': Unit,
    }
    obj_dict = {
        'correct_variable': Variable,
        'wrong_variable': Variable
    }

    qc_dict = {}
    for name in app.config['QUESTIONCATAGORIES']:
        qc = QuestionCategory(name = name)
        qc_dict[name] = qc
        db.session.add(qc)
    db.session.commit()

    for question_config in app.config['QUESTIONS']:
        config = {}
        config['name'] = question_config['name']
        config['body'] = question_config['body']
        qc = qc_dict[question_config['category']]
        config['category_id'] = qc.id
        if 'answer_command' in question_config:
            config['answer_command'] = question_config['answer_command']
        for key, value in obj_list_dict.items():
            if key in question_config:
                obj_list = []
                config[key] = obj_list
                for obj_str in question_config[key]:
                    obj = value.query.filter_by(
                        name = obj_str
                    ).first()
                    if obj:
                        obj_list.append(obj)
                    else:
                        print "failed, %s not found" % obj_str
        for key, value in obj_dict.items():
            if key in question_config:
                obj_str = question_config[key]
                obj = value.query.filter_by(
                    name = obj_str
                ).first()
                if obj:
                    config[key] = obj
                else:
                    print "failed, %s not found" % obj_str
        db.session.add(Question(
            **config
        ))
    db.session.commit()

@manager.command
def create_exercise():
    for exe_config in app.config['EXERCISE']:
        config = {}
        config['name'] = exe_config['name']
        config['open_date'] = datetime.today() - relativedelta(years=1)
        config['close_date'] = datetime.today() + relativedelta(years=1)
        questions = []
        for q in exe_config['questions']:
            question = Question.query.filter_by(
                name = q
            ).first()
            if question:
                questions.append(question)
            else:
                print "failed, %s not found" % q
        config['questions'] = questions
        exercise = Exercise(**config)
        db.session.add(exercise)
    for exe_config in app.config['EXERCISE']:
        config = {}
        config['name'] = exe_config['name'] + ' (expired)'
        config['open_date'] = datetime.today() - relativedelta(years=2)
        config['close_date'] = datetime.today() - relativedelta(years=1)
        questions = []
        for q in exe_config['questions']:
            question = Question.query.filter_by(
                name = q
            ).first()
            if question:
                questions.append(question)
            else:
                print "failed, %s not found" % q
        config['questions'] = questions
        exercise = Exercise(**config)
        db.session.add(exercise)
    db.session.commit()

if __name__ == '__main__':
    manager.run()
