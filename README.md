Flask teaching site framwork
============================

This is the exercise page for quantum chemistry. 
It is designed to automize the exercise evaluation using Flask/SQLAlchemy.

The following command should be executed before running the server
* pip install -r requirements.txt (assuming proper enviroment is setup)
* python3 run.py

The admin is set to be 
* account: admin
* passwd: admin
(see config.py)

__NOTE: PLEASE CHANGE THE EMAIL WITH CORRECT LOGIN__
It is necessary for sending email of validation code

The default admin address need to be changed to have gmail response for user password reset

# How to assemble an exercise sheet

Basically, to create an exercise, you have to create questions at first.
Questions belong to QuestionCategories and use Variables and Units. 
Units belongs to UnitCategories.

To create all of this, you have to log in as an admin. 

## How to create a Variable

Variables has following properties:

- Category - Integer, Float, String, Unit
- Variable name - You have to name variable somehow and refer to it later with this name
- Variable description - Arbitrary description seen only by other admins
- Constraint - Can be a range (for floats), or a list (for ints)

Currently only a single Variable can be assigned to a single Question. 

## How to create a Question

A Question has these parameters:

- Category - One of QuestionCategories
- Title - A name of the question
- Question text - All Variables used in the question text has to be surrounded by '\_', e.g. \_X\_. When the question is rendered, a random value from range specified in Constraing parameter of a Variable is rendered instead of the Variable. If you need to use math symbols, you have to put all the math between double dollar signs.
- Answer - A text or a command. If you need to use mathematical functions here, do not put them between double dollar signs as the text here is not rendered with MathJax but with Sympy. Variables used still need to be surrounded by \_.
- Text Variables - Here, state all Variables used in this question.

Variables used in the question with multiple choices can not be of type range, they have to be a list.

## How to create a QuestionCategory

The only purpose of QuestionCategories is to sort questions. 
You may want to create a category for numerical questions with/without units,
string questions or group questions by topics of lessons. 
Questions are usually refered to as QuestionCategory-Question.name.

