from teaching_site import app, db
from flask import render_template, redirect, url_for, flash, session, abort, request
from teaching_site.exercise.models import Exercise, Sheet, Question
from teaching_site.exercise.form import QuestionForm
from teaching_site.user.decorators import login_required, only_from, admin_required
from teaching_site.user.models import User
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

@app.route('/render/<int:id>')
@app.route('/render/<int:id>/<int:seed>')
@admin_required
def render(id, seed=None):
    render_name = 'render single question'
    question = Question.query.filter_by(
        id=id
    ).first()
    
    exercise = Exercise.query.filter_by(
        name = render_name,
    ).first()
    if exercise:
        setattr(exercise, 'open_date', datetime.today() - relativedelta(months=1)),
        setattr(exercise, 'close_date', datetime.today() + relativedelta(months=1)),
        setattr(exercise, 'questions', [question])
    else:
        exercise = Exercise(
            name = render_name,
            open_date = datetime.today() - relativedelta(months=1),
            close_date = datetime.today() + relativedelta(months=1),
            active = False,
            questions = [question]
        )
        db.session.add(exercise)
    db.session.commit()
    if seed is None:
        user = User.query.filter_by(
            username = session['username']
        ).first()
        seed = user.random_seed
    return redirect(url_for('exercise', id=exercise.id, seed=seed))


@app.route('/exercise')
@app.route('/exercise/<int:id>', methods=['GET', 'POST'])
@app.route('/exercise/<int:id>/<int:seed>', methods=['GET', 'POST'])
@login_required
def exercise(id=None, seed=None):

    error = None
    flashed = False
    last_edited = True
    submit = False
    submitted = False

    if id is None:
        return redirect(url_for('index'))
    exercise = Exercise.query.filter_by(
        id=id,
    ).first_or_404()
    user = User.query.filter_by(
        username = session['username']
    ).first()
    if not exercise.active and not user.is_admin:
        abort(404)
    if user.is_admin:
        msg = 'Admin message: '
        if exercise.active:
            msg +=  'This exercise is visible to user on ' + \
                    'open_date %s' %\
                    exercise.open_date.strftime("%Y/%m/%d-%H:%m")
            flash(msg)
        else:
            msg += 'Not visible exercise'
            flash(msg)

    kwargs = {
        'exercise': exercise,
        'id': id,
        'readonly': True,
    }

    now = datetime.now()
    practice = False

    if seed is None:
        seed = user.random_seed

    if seed and seed != user.random_seed or user.is_admin:
        if now > exercise.close_date or user.is_admin:
            practice = True
            kwargs['readonly'] = False
        else:
            seed = user.random_seed
    else:
        seed = user.random_seed

    forms = []
    status_list = []
    points = []
    ans_msgs = []

    optional_list = []
    numerical_list = []
    no_answer_list = []
    for q in exercise.questions:
        answer = q.evaluate(seed)
        if q.no_answer:
            no_answer_list.append(q)
        elif type(answer) is float:
            numerical_list.append(q)
        else:
            optional_list.append(q)
    question_list = optional_list
    question_list.extend(numerical_list)
    question_list.extend(no_answer_list)

    for i in range(len(question_list)):

        question = question_list[i]

        ans_msg = ''
        status= ''

        sheet = Sheet.query.filter_by(
            user_id = user.id,
            exercise_id = exercise.id,
            question_id = question.id
        ).first()
        if not sheet and not question.no_answer:
            sheet = Sheet(
                user_id = user.id,
                exercise_id = exercise.id,
                question_id = question.id
            )
        if not question.no_answer:
            if sheet.point is not None:
                submitted = True
                if now < exercise.close_date:
                    kwargs['readonly'] = True
        else:
            try:
                if last_edited:
                    last_edit = sheet.edit_date
                    flash('Last edit on %s'\
                          % last_edit.strftime("%Y/%m/%d, %H:%M"))
                    last_edited = False
            except:
                pass

        name = 'form%d' % i
        form = QuestionForm(
            exercise_id = exercise.id,
            question_id = question.id,
            user_id = user.id,
            prefix = name,
            obj = sheet
        )
        forms.append(form)
        if (now > exercise.open_date and now < exercise.close_date)\
        and not submitted or practice:
            if not submitted:
                kwargs['readonly'] = False
            if form.validate_on_submit() and not question.no_answer:
                if 'submit' in request.form.keys():
                    submit = True
                sheet.number = form.number.data
                sheet.option1 = form.option1.data
                sheet.option2 = form.option2.data
                sheet.option3 = form.option3.data
                sheet.option4 = form.option4.data
                sheet.option5 = form.option5.data
                edit_time = datetime.now()
                sheet.edit_date = edit_time

                if not practice:
                    try:
                        db.session.add(sheet)
                        db.session.flush()
                    except:
                        error = "Answer can not be saved..., " +\
                                "please contact coure administrator"
        
                    if sheet.id:
                        db.session.commit()
                        if not flashed:
                            if not submit:
                                flash('Answers has been saved on %s' % \
                                    edit_time.strftime("%Y/%m/%d, %H:%M"))
                            else: 
                                flash('Your answer has been submitted')
                            flashed = True
                        if sheet.number is not None:
                            ans_msg = "Your answer %e was saved." \
                                % (sheet.number)
                            status = 'text-info'
                        elif sheet.option1 or sheet.option2 \
                        or sheet.option3 or sheet.option4 \
                        or sheet.option5:
                            mask = np.array([
                                sheet.option1,
                                sheet.option2,
                                sheet.option3,
                                sheet.option4,
                                sheet.option5,
                            ])
                            for m in range(len(mask)):
                                if mask[m] is None:
                                    mask[m] = False
                             
                            choice = np.ma.masked_array(
                                np.arange(1,6), ~mask)
                            n_options = len(
                                question.render(seed)[1])
                            tried = np.array([
                                c for c in choice[:n_options] if c])
                            tried = tried.tolist()
                            ans_msg = "Your choice option:"
                            ans_msg += str(tried)
                            ans_msg += " was saved."
                            status = 'text-info'
                else:
                    if not flashed:
                        flash('Practice result will not be saved')
                        if submit:
                            flash('Results submitted')
                        flashed = True
        if now > exercise.close_date or practice or submit or submitted:
            point = 0.0
            status = 'text-danger'
            answer =  question.evaluate(seed)
            if not question.no_answer:
                if type(answer) is float:
                    if sheet.number:
                        tried = float(sheet.number)
                        if answer == 0 and abs(tried) < 1E-3:
                            point = 1.0
                            ans_msg = "Your answer is correct!"
                            status = 'text-success'
                        elif abs((tried - answer)/answer) < 0.1:
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
                        sheet.option1,
                        sheet.option2,
                        sheet.option3,
                        sheet.option4,
                        sheet.option5,
                    ])
                    for m in range(len(mask)):
                        if mask[m] is None:
                            mask[m] = False
                     
                    n_options = len(question.render(seed)[1])
                    choice = np.ma.masked_array(np.arange(1,6), ~mask)
                    tried = np.array([c for c in choice[:n_options] if c])-1
                    tried = tried.tolist()
                    
                    if not (sheet.option1 or sheet.option2 \
                    or sheet.option3 or sheet.option4 or sheet.option5):
                        if not question.no_answer:
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
                                ans_msg += " Negative points to balence expectation value."

            if not question.no_answer:
                ans_msg += " You've got %4.2f point." % (round(point, 3))
                points.append(round(point, 3))

                sheet.point = point
            if not practice:
                try:
                    db.session.commit()
                except:
                    error = "Evaluated results can not be saved, " +\
                            " please contact course administrator."
    
                if not flashed:
                    flash('This exercise is already closed.')
                    flashed = True
            else:
                if not flashed:
                    flash('Practice results will not be saved.')
                    flashed = True
                
        if now < exercise.open_date:
           if not flashed:
               error = "Exercise not is opened yet, "\
                       + "it is set to be open on %s"\
                       % exercise.open_date.strftime("%Y/%m/%d, %H:%M")
               flashed = True
        status_list.append(status)
        ans_msgs.append(ans_msg)
    kwargs['status_list'] = status_list
    kwargs['points'] = points
    kwargs['ans_msgs'] = ans_msgs
    kwargs['forms'] = forms
    kwargs['error'] = error
    kwargs['seed'] = seed
    kwargs['practice'] = practice
    kwargs['question_list'] = question_list
    return render_template('exercise/render.html', **kwargs)
