from teaching_site import app, db
from flask import render_template, redirect, url_for, flash, session, abort, request
from teaching_site.exercise.models import Exercise, Sheet
from teaching_site.user.decorators import login_required, admin_required
from teaching_site.user.models import User
from datetime import datetime
import numpy as np
from numpy.random import randint
import pandas as pd

@app.route('/')
@app.route('/index')
def index():
    exercises_all = Exercise.query.all()
    exercises = []
    if 'is_admin' in session and session['is_admin']:
        exercises = exercises_all
    else:
        for i in range(len(exercises_all)):
            exercise = exercises_all[i]
            if exercise.open_date < datetime.now():
                if exercise.active:
                    exercises.append(exercises_all[i])
    eid = [e.id for e in exercises]
    nq = [len(e.questions) for e in exercises]
    enames = [e.name for e in exercises]
    dates = [e.close_date for e in exercises]
    kwargs = {'eid': eid, 'nq': nq, 'enames': enames, 'dates': dates}
    return render_template('home/index.html', **kwargs)

@app.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(
        username = session['username']
    ).first()
    exercises_all = Exercise.query.all()
    exercises = []
    for i in range(len(exercises_all)):
        if exercises_all[i].close_date < datetime.now()\
        and exercises_all[i].active:
            exercises.append(exercises_all[i])
    results = []
    total = 0
    for exercise in exercises:
        sheets = Sheet.query.filter_by(
            exercise_id = exercise.id,
            user_id = user.id,
        )
        points = np.array(
            [float(s.point) 
             for s in sheets if s.point is not None]
        ).mean()*100
        if points > 0:
            total += points
        results.append(max(round(points, 3), 0))
    total /= float(len(exercises))
    seed = randint(1, 10000)
    kwargs = {
        'user': user, 
        'exercises': exercises, 
        'results': results,
        'seed': seed,
        'total': total,
    }
    return render_template('home/profile.html', **kwargs)

@app.route('/score')
@admin_required
def score():
    # filter out admins
    users = User.query.filter_by(is_admin = False).all()
    exercises = Exercise.query.filter(
        Exercise.close_date <= datetime.now()
    ).all()
    #sheets = Sheets.query.all()

    index = [user.fullname for user in users if user is not None]
    dtype = [
        ('Exercise %02d' % (i+1), 'float32') \
        for i in range(len(exercises))
    ]
    score = np.zeros(len(index), dtype=dtype)
    for u in range(len(users)):
        user = users[u]
        for e in range(len(exercises)):
            exercise = exercises[e]
            sheets = Sheet.query.filter_by(
                user_id = user.id,
                exercise_id = exercise.id
            ) 
            score[u][e] = np.array([
                float(s.point) 
                for s in sheets if s.point is not None
            ]).sum() / float(len(exercise.questions))
    data = pd.DataFrame(score, index = index)
    return render_template('home/score.html', data = data.to_html())
