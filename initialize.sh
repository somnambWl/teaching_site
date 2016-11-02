#!/bin/bash

rm teaching_site/data/course_data.db
rm security.log

(python manage.py init &&
echo "db created")
(python manage.py create_unit &&
echo "units created")
(python manage.py create_variable &&
echo "variables created")
(python manage.py create_question &&
echo "questions created")
(python manage.py create_exercise &&
echo "exercise created")
