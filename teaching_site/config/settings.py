import os
from datetime import datetime

# app setting
DEBUG = True
# database setting
SQLALCHEMY_TRACK_MODIFICATIONS = True
# upload letting
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOADED_IMAGES_DEST = os.path.join(APP_ROOT, 'static/images')
UPLOADED_IMAGES_URL = "/static/images/"
# email setting
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_TLS = False
MAIL_USE_SSL= True

# initial setup for question data
# name: m, kg, s, A, K, mol, cd
UNIT_CATAGORIES = {
    'unitless':   [ 0,  0,  0,  0,  0,  0,  0],
    'length':     [ 1,  0,  0,  0,  0,  0,  0],
    'mass':       [ 0,  1,  0,  0,  0,  0,  0],
    'time':       [ 0,  0,  1,  0,  0,  0,  0],
    'charge':     [ 0,  0,  1,  1,  0,  0,  0],
    'temperatur': [ 0,  0,  0,  0,  1,  0,  0],
    'mole':       [ 0,  0,  0,  0,  0,  1,  0],
    'area':       [ 2,  0,  0,  0,  0,  0,  0],
    'volume':     [ 3,  0,  0,  0,  0,  0,  0],
    'frequency':  [ 0,  0, -1,  0,  0,  0,  0],
    'period':     [ 0,  0,  1,  0,  0,  0,  0],
    'energy':     [ 2,  1, -2,  0,  0,  0,  0],
    'force':      [ 1,  1, -2,  0,  0,  0,  0],
    'pressure':   [-1,  1, -2,  0,  0,  0,  0],
}

UNITS = [
    # energy
    ['eV', 'electron volt', 'eV', 1.602e-19, 'energy'],
    ['kcal/mol', 'kilocalories per mol', r'\(\frac{\rm kcal}{\rm mol}\)', 6.948e-21, 'energy'],
    ['kJ/mol', 'kilojoule per mol', r'\(\frac{\rm kJ}{\rm mol}\)', 1.660e-21, 'energy'],
    ['Eh', 'Hartree', r'\(E_h\)', 4.340e-18, 'energy'],
    ['J', 'Joule', 'J', 1.0, 'energy'],
    # length
    ['m', 'meter', r'$m$', 1.0, 'length'],
    ['nm', 'nanometer', r'\(nm\)', 1e-9, 'length'],
    ['pm', 'picometer', r'\(pm\)', 1e-12, 'length'],
    ['ang', 'Angtrom', r'\(\rm\AA\)', 1e-10, 'length'],
    ['a0', 'Bohr', r'\(a_0\)', 5.292e-11, 'length'],
    # mass
    ['kg', 'kilogram', r'\(kg\)', 1.0, 'mass'],
    ['g', 'gram', r'\(g\)', 1e-3,'mass'],
    ['Da', 'Dalton', 'Da', 1.660e-27, 'mass'],
    # time
    ['s', 'second', r'\(s\)',1.0, 'time'],
    ['Hz', 'Hertz', 'Hz', 1.0, 'frequency'],
    ['T', 'period', 'T', 1.0, 'period'],
]

VARIABLES = [
    {'name': 'ni',
     'category': 'int',
     'description': 'initial level of hydrogen atom',
     'constraint': r'[0, 1, 2]'},
    {'name': 'nf',
     'category': 'int',
     'description': 'final level of hydrogen atom',
     'constraint': r'[3, 4, 5]'},
    {'name': 'unite',
     'category': 'float',
     'description': 'requsted unit for answer'},
    {'name': 'x',
     'category': 'float',
     'description': 'some float number, range',
     'constraint': r'(5.3, 8.9)'},
    {'name': 'y',
     'category': 'float',
     'description': 'some float number, list',
     'constraint': r'[1.1, 2.2, 3.3, 4.4]'},
    {'name': 'correct_option',
     'category': 'str',
     'description': 'some correct strings',
     'constraint': r"['correct1', 'correct2', 'correct3', 'correct4', 'correct5']"},
    {'name': 'wrong_option',
     'category': 'str',
     'description': 'some wrong string',
     'constraint': r"['wrong1', 'wrong2', 'wrong3', 'wrong4', 'wrong5']"},
    {'name': 'correct_option_single',
     'category': 'str',
     'description': 'some correct strings single',
     'constraint': r"['correct1']"},
    {'name': 'wrong_option_single',
     'category': 'str',
     'description': 'some wrong string single',
     'constraint': r"['wrong1', 'wrong2', 'wrong3', 'wrong4', 'wrong5']"},
    {'name': 'E0',
     'category': 'unit',
     'description': 'energy to convert',
     'units': ['eV', 'kcal/mol', 'kJ/mol', 'Eh']},
    {'name': 'energy',
     'category': 'unit',
     'description': 'energy to convert',
     'units': ['eV', 'kcal/mol', 'kJ/mol', 'Eh']},
    {'name': 'mass',
     'category': 'float',
     'description': 'mass with unit',
     'constraint': r'(0.1, 100)',
     'units': ['kg', 'g', 'Da']},
    {'name': 'length',
     'category': 'float',
     'description': 'length with unit',
     'constraint': r'(0.1, 100)',
     'units': ['m', 'nm']},
    {'name': 'time',
     'category': 'float',
     'description': 'time with unit',
     'constraint': r'[1]',
     'units': ['s']}
]

QUESTIONCATAGORIES = [
    'Test questions',
]

QUESTIONS = [
    {'name': 'test numeric question',
     'body': r'compute $$\big(\cos(_x_)^2 + e^{_y_}\big)\times (_x_+_y_)$$',
     'answer_command': r'(cos(_x_)**2 + exp(_y_)) * (_x_+_y_)',
     'text_variables': ['x', 'y'],
     'category': 'Test questions'},
    {'name': 'test choice question',
     'body': r'which is the correct statment',
     'correct_variable': 'correct_option',
     'wrong_variable': 'wrong_option',
     'category': 'Test questions'},
    {'name': 'test single choice question',
     'body': r'which is the correct statment',
     'correct_variable': 'correct_option_single',
     'wrong_variable': 'wrong_option_single',
     'category': 'Test questions'},
    {'name': 'test unit conversion',
     'body': 'convert _energy_ to other unit. Give you answer in _unit_',
     'text_variables': ['energy'],
     'answer_command': '_energy_',
     'answer_units': ['eV', 'kcal/mol', 'kJ/mol', 'Eh'],
     'category': 'Test questions'},
    {'name': 'test unit operation',
     'body': r'given \(m=\)_mass_, \(v=\frac{l}{t}\), where \(l=\)_length_, and \(t=\)_time_, comput \(\frac{1}{2}mv^2\). Give your anser in _unit_',
     'text_variables': ['mass', 'length', 'time'],
     'answer_command': '0.5 * _mass_ * (_length_/_time_)**2',
     'answer_units': ['eV', 'kcal/mol', 'kJ/mol', 'Eh'],
     'category': 'Test questions'},
]

EXERCISE = [
    {'name': 'Test exercise',
     'questions': ['test numeric question', 
                   'test choice question',
                   'test single choice question',
                   'test unit conversion',
                   'test unit operation'],
    },
]

