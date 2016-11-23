from teaching_site import db
from numbers import Number
from copy import deepcopy
import numpy as np
from sympy.parsing.sympy_parser import parse_expr
import ast

def convert(from_unit, to_unit):
    from_unit = deepcopy(from_unit)
    if from_unit.name != to_unit.name:
        factor = from_unit.SI_value / float(to_unit.SI_value)
        from_unit._value = from_unit._value * factor
    return from_unit._value

class UnitCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # SI base units
    m = db.Column(db.Integer)
    kg = db.Column(db.Integer)
    s = db.Column(db.Integer)
    A = db.Column(db.Integer)
    K = db.Column(db.Integer)
    mol = db.Column(db.Integer)
    cd = db.Column(db.Integer)
    variations = db.relationship(
        'Unit',
        backref='category', 
        lazy='dynamic')

    def __repr__(self):
        return self.name

    def __init__(self, name='', 
        m=0, kg=0, s=0, A=0, K=0, mol=0, cd=0
    ):
        self.name = name
        self.m =  m 
        self.kg = kg 
        self.s = s 
        self.A = A 
        self.K = K 
        self.mol = mol
        self.cd = cd 
        self._value = np.array([m, kg, s, A, K, mol, cd])

    def _get_value(self):
        if not hasattr(self, '_value'):
            self._value = np.array([
                self.m,
                self.kg,
                self.s,
                self.A,
                self.K,
                self.mol,
                self.cd,
            ])
        return self

variable_units = db.Table(
    'variable_units',
    db.Column(
        'unit_id', 
        db.Integer, 
        db.ForeignKey('unit.id')),
    db.Column(
        'variable_id', 
        db.Integer, 
        db.ForeignKey('variable.id')),
)

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    face = db.Column(db.String(100))
    SI_value = db.Column(db.Float)
    category_id = db.Column(
        db.Integer, 
        db.ForeignKey('unit_category.id'),
        nullable=False)
    active_variables = db.relationship(
        'Variable',
        secondary = variable_units,
        backref = db.backref('units', lazy='dynamic')
    )

    def __init__(self, 
        name='', fullname='', face='', SI_value=1., category=None
    ):
        self.fullname = fullname
        self.name = name
        if not face:
            face = name
        self.face = face
        self.SI_value = SI_value
        if isinstance(category, UnitCategory):
            self.category = category
        else:
            try:
                category_type = UnitCategory.query.filter_by(
                    name = category,
                ).first()
                if category_type:
                    self.category = category_type
            except:
                self.category = None

    def __repr__(self):
        return "%s (%s)" % (self.name, self.category.name)
 
    def _copy(self):
        new = Unit(
            fullname = self.fullname,
            name = self.name,
            face = self.face,
            SI_value = self.SI_value,
            category = self.category
        )
        new._value = self._value
        return new

    def from_SI(self, value):
        return float(value) / float(self.SI_value)

    def get_face(self):
        return "%s (%s)" % (self.fullname, self.face)

    def value(self):
        self._get_value()
        return float(self._value) * float(self.SI_value)

    def face_value(self):
        self._get_value()
        return float(self._value)

    def to(self, other):
        assert type(self) is type(other)
        self._get_value()
        other._get_value()
        out = deepcopy(other)
        if self.name != other.name:
           out._value = self._value * convert(self, other) 
        return out

    def _get_value(self):
        try:
            self.category._get_value()
        except:
            pass
        if not hasattr(self, '_value'):
            self._value = 1.
        return self

    def _add_sub(self, other, operation):

        assert type(self) is type(other)
        assert self.category.name == other.category.name

        self._get_value()
        other._get_value()
        out = self._copy

        if operation == '+':
            out._value = out._value + convert(other, out)
        elif operation == '-':
            out._value = out._value - convert(other, out)

        return out

    def _mul_div(self, other, operation):

        self._get_value()
        out = self._copy()

        if isinstance(other, Number):
            out._value = other * out._value
            new_unit = out
            
        elif type(out) is type(other):

            other._get_value()
 
            new_unit_type = out.category.name + operation + other.category.name
            new_unit_name = out.name + operation + other.name

            if operation == '*':
                new_base = out.category._value + other.category._value
                SI_value = out.SI_value * other.SI_value
                _value = out._value * other._value

            elif operation == '/':
                new_base = out.category._value - other.category._value
                SI_value = out.SI_value / float(other.SI_value)
                _value = out._value / float(other._value)

            new_unit_category = UnitCategory(
                new_unit_type,
                *new_base.tolist()
            )
            new_unit = Unit(
                name = new_unit_name, 
                category = new_unit_category
            )
            new_unit.SI_value = SI_value
            new_unit._value = _value

        else:
            raise TypeError

        return new_unit

    def __add__(self, other):
        return self._add_sub(other, '+')

    def __radd__(self, other):
        return self._add_sub(other, '+')

    def __sub__(self, other):
        return self._add_sub(other, '-')

    def __rsub__(self, other):
        return self._add_sub(other, '-')
        
    def __mul__(self, other):
        return self._mul_div(other, '*')

    def __rmul__(self, other):
        return self._mul_div(other, '*')

    def __div__(self, other):
        return self._mul_div(other, '/')

    def __rdiv__(self, other):
        return self._mul_div(other, '/')

    def SI_face(self):
        self._get_value()
        key = ['m', 'kg', 's', 'A', 'K', 'mol', 'cd']
        out = r'% 5.2E $\times$' % (self._value * self.SI_value)
        for i in range(len(key)):
            if self.category._value[i] != 0:
                p = self.category._value[i]
                if p != 1:
                    out = out + r' %s$^{%s}$' % (key[i], p)
                else:
                    out = out + r' %s' % key[i]
        return out

class Variable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    question_id = db.Column(
         db.Integer,
         db.ForeignKey('question.id'))

    # constraints, one of the three below
    # tuple string: '(min, max)'
    # list string: '[value1, value2, value3]'
    # dict string for dependent variable value: 
    # "{'val1_var1': [value1, value2, value3], 
    #   'val2_var1: (min, max)'
    constraint = db.Column(db.Text)

    def __init__(self,
        name = '',
        description = '',
        category = '',
        constraint = '',
        units = '',
    ):
        self.name         = name  
        self.description  = description 
        self.category     = category
        self.constraint   = constraint
        self.units        = units

    def __repr__(self):
        base = "%s %s" % (self.name, self.category)
        if self.question is not None\
        or len(self.correct_question) > 0\
        or len(self.wrong_question) > 0:
            return base + " (used)"
        else:
            return base + " (available)"

    def draw(self, seed):
        rs = np.random.RandomState(seed)
        if self.constraint:
            c = ast.literal_eval(self.constraint)
        else:
            c = []
        if self.category == 'float':
            if type(c) is tuple:
                if len(c) == 2:
                    value = rs.rand() * (c[1] - c[0]) + c[0]
                elif len(c) == 3:
                    value = rs.choice(np.arange(*c))
                else:
                    raise TypeError
            elif type(c) is list:
                if len(c) > 0:
                    value = rs.choice(c)
                else:
                    raise TypeError
            elif type(c) is dict:
                raise TypeError
            return value
        elif self.category == 'int':
            if type(c) is tuple:
                value = rs.choice(range(*c))
            elif type(c) is list:
                value = rs.choice(c)
            elif type(c) is dict:
                raise TypeError
            return value
        elif self.category == 'str':
            assert type(c) is list
            return rs.choice(c)
        elif self.category == 'unit':
            unit = rs.choice(self.units.all())
            return unit.SI_value
        else:
            raise TypeError

    def value(self, seed=None):
        rs = np.random.RandomState(seed)
        value = self.draw(seed)
        if self.category == 'float' and len(self.units.all()) > 0:
            unit = rs.choice(self.units.all())
            value = value * unit.SI_value
        return value

    def render(self, seed = None):
        rs = np.random.RandomState(seed)
        if self.category != 'unit':
            value = self.draw(seed)
            if 100 > value and value >= 1:
                value = "%.2f" % value
            elif 1 > value and value >= 0.1:
                value = "%.4f" % value
            else:
                value = "%9.3E" % value
            if hasattr(self, 'units') and len(self.units.all()) > 0:
                unit = rs.choice(self.units.all())
                value = value + " %s" % unit.name
            return value
        else:
            unit = rs.choice(self.units.all())
            value = unit.get_face()
            return value

    def get_list(self):
        assert hasattr(self, 'constraint')
        c = ast.literal_eval(self.constraint)
        assert type(c) is list
        return c

class QuestionCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    questions = db.relationship(
        'Question',
        backref='category',
        lazy='dynamic',
    )

    def __repr__(self):
        return self.name

question_unit_text = db.Table(
    'question_unit_text',
    db.Column(
        'unit_id',
        db.Integer,
        db.ForeignKey('unit.id')),
    db.Column(
        'question_id',
        db.Integer,
        db.ForeignKey('question.id')),
)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    answer_command = db.Column(db.Text)
    no_answer = db.Column(db.Boolean, default=False)
    # relationship with question
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('question_category.id'))

    text_variables = db.relationship(
        'Variable',
        backref = 'question',
        primaryjoin = 'Question.id==Variable.question_id',
        lazy='dynamic')

    answer_units = db.relationship(
        'Unit',
        secondary = question_unit_text,
        backref = db.backref('answer_questions', lazy='dynamic')
    )

    correct_variable_id = db.Column(db.Integer, 
        db.ForeignKey('variable.id'))
    correct_variable = db.relationship(
        Variable, 
        backref = db.backref('correct_question', order_by=id),
        foreign_keys=correct_variable_id)

    wrong_variable_id = db.Column(db.Integer, 
        db.ForeignKey('variable.id'))
    wrong_variable = db.relationship(
        Variable, 
        backref = db.backref('wrong_question', order_by=id),
        foreign_keys=wrong_variable_id)

    def __init__(self, name='', body='', answer_command='',
        category_id = None, text_variables=[], correct_variable_id = None,
        correct_variable = None, wrong_variable_id = None,
        wrong_variable = None, answer_units=[],
    ):
        self.name = name
        self.body = body
        self.answer_command = answer_command
        self.category_id = category_id
        if len(text_variables) > 0 and type(text_variables[0]) is str:
            variable_list = []
            for i in range(len(text_variables)):
                var = Variable.query.filter_by(
                    name = text_variables[i]
                ).first()
                variable_list.append(var)
            self.text_variables = variable_list
        else:
            self.text_variables = text_variables
        self.correct_variable_id = correct_variable_id
        if type(correct_variable) is str:
            var = Variable.query.filter_by(
                name = correct_variable
            ).first()
            self.correct_variable = var
        else:
            self.correct_variable = correct_variable
        self.wrong_variable_id = wrong_variable_id
        if type(wrong_variable) is str:
            var = Variable.query.filter_by(
                name = wrong_variable
            ).first()
            self.wrong_variable = var
        else:
            self.wrong_variable = wrong_variable
        self.answer_units = answer_units

    def __repr__(self):
        if self.category:
            return "%s %s" % (self.category.name, self.name)
        else:
            return self.name

    def render(self, seed, options=5):
        seed = seed + self.id
        rs = np.random.RandomState(seed)
        text = self.body
        for i in range(len(self.text_variables.all())):
            var = self.text_variables[i]
            pattern = '_' + var.name + '_'
            text = text.replace(pattern, 
                str(var.render(seed+i)))

        if self.answer_units:
            unit_rs = np.random.RandomState(seed+1)
            unit = unit_rs.choice(self.answer_units)
            pattern = '_unit_'
            face = unit.get_face()
            text = text.replace(pattern, face)
        
        option_list = []
        if self.correct_variable and self.wrong_variable:
            option_list = []
            correct_list = rs.permutation(
                self.correct_variable.get_list()
            ).tolist()
            wrong_list = rs.permutation(
                self.wrong_variable.get_list()
            ).tolist()
            ind = rs.randint(0, len(correct_list))
            option_list.append(correct_list.pop(ind))
            correct_list.extend(wrong_list)
            option_list.extend(
                rs.permutation(correct_list)[:options - 1]
            )
        return text, rs.permutation(option_list)
            
    def evaluate(self, seed):
        seed = seed + self.id
        rs = np.random.RandomState(seed)
        if self.answer_command:
            answer = self.answer_command
            for i in range(len(self.text_variables.all())):
                var = self.text_variables[i]
                name = '_' + var.name + '_'
                answer = answer.replace(name, str(var.value(seed+i)))
            SI_answer = float(parse_expr(answer))
            if self.answer_units:
                unit_rs = np.random.RandomState(seed+1)
                unit = unit_rs.choice(self.answer_units)
                SI_answer = unit.from_SI(SI_answer)
            return SI_answer
        else:
            answer_list = []
            option_list = self.render(seed)[1]
            for i in range(len(option_list)):
                if option_list[i] in self.correct_variable.get_list():
                    answer_list.append(i)
            return answer_list
