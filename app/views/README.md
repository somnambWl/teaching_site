About this folder
-----------------

Views collect variables and selects a template for URL adresses.
URL adress is specified at the beginning and end of each view function.
At the end of view function a HTML template from __templates__ folder is specified.
A view sends variables to a template and it is rendered.
A view can also receive variables from a template, 
e.g. an exercise page is rendered once with empty forms
and second time when user submit their results.
Variables from templates are sent in form of query parameters (after question mark in URL adress) or in form.
They are obtained using _requests_ package.

This folder contain two different types of views.
We use _Flask-Admin_ package which defines views for admins in a different way than pure _Flask_, 
so _admin.py_ and *admin_home.py* are different from other views.
Homepage for admin also has to be specified before loading views for admin,
so it is defined in a separate file.

Inside this folder
------------------

- admin\_home.py - Home view for admin which contains summary table of enrolled students and their results
- admin.py - All other admin views which let them manipulate the database
- exercise.py - Views for exercises, probably the most complicated one
- home.py - Views for index page
- question.py - Views for questions
- user.py - Views for users
