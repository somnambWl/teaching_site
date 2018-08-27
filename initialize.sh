#!/bin/bash

rm teaching_site/data/course_data.db
rm security.log

update_py=$(find -name "*.py")

for f in $update_py; do 2to3 -l -w $f; done

echo "updated py 2.7 to py 3.5"

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
