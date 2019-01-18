
from flask import render_template, redirect, url_for, flash, session, \
        abort, request

from app import app, db

@app.route('/question')
@app.route('/question/<int:id>')
def question(id=None):
    if id is None:
        id = 0
        return render_template('question/question_list.html', id=0)
    else:
        return render_template('question/question_id.html', id=id)
