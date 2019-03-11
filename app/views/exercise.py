
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

from flask import render_template, redirect, url_for, flash, session, \
        abort, request

from app import app, db
from app.models.exercise import Exercise, Sheet, Question
from app.forms.exercise import QuestionForm
from app.common.decorators import login_required, only_from, admin_required
from app.models.user import User
from app.common.tools import evaluate

@app.route('/reevaluate')
@app.route('/reevaluate/<int:id>')
@admin_required
def reevaluate(id=None):
    if id is None:
        flash('Reevaluate all exercise sheets')
        for sheet in Sheet.query.all():
            evaluate(sheet.question, sheet, sheet.user.random_seed)
    else:
        sheet = Sheet.query.filter_by(id=id).first()
        flash(f"Reevaluate sheet for user {sheet.user}")
        evaluate(sheet.question, sheet, sheet.user.random_seed)
    return redirect('admin/sheet')
    

@app.route('/render/<int:id>')
@admin_required
def render(id, seed=None):
    seed = request.form.get("seed", None)
    render_name = 'Render a single question'
    question = Question.query.filter_by(id=id).first()
    exercise = Exercise.query.filter_by(name=render_name).first()
    if exercise:
        setattr(exercise, 'open_date', 
            datetime.today() - relativedelta(months=1)),
        setattr(exercise, 'close_date', 
            datetime.today() + relativedelta(months=1)),
        setattr(exercise, 'questions', [question])
    else:
        exercise = Exercise(
                name = render_name,
                open_date = datetime.today() - relativedelta(months=1),
                close_date = datetime.today() + relativedelta(months=1),
                active = False,
                questions = [question])
        db.session.add(exercise)
    db.session.commit()
    if seed is None:
        user = User.query.filter_by(username = session['username']).first()
        seed = user.random_seed
    return redirect(url_for('exercise', id=exercise.id, seed=seed))


@app.route('/exercise')
@app.route('/exercise/<int:id>', methods=['GET', 'POST'])
@login_required
def exercise(id=None):
    seed = request.form.get("seed", None)
    error = None
    flashed = False
    last_edited = True
    submit = False
    submitted = False
    if id is None:   # If there is no exercise with such an ID 
        return redirect(url_for('index'))   # Go back to the main page
    # Get the exercise by the ID
    exercise = Exercise.query.filter_by(id=id).first_or_404()
    # Get user by their username
    user = User.query.filter_by(username=session['username']).first()
    # User has to be validated to do exercises
    if not user.validated:
        return redirect(url_for('validate'))
    # The exercise has to be active, users can not do them after 
    # the time limit for an exercise runned out.
    if not exercise.active and not user.is_admin:
        abort(404)
    # However, if user is an admin, he can view an exercise anytime.
    if user.is_admin:
        msg = 'Admin message: '
        if exercise.active:
            msg += 'This exercise is visible to user on ' + \
                    f'{exercise.open_date.strftime("%Y/%m/%d-%H:%m")}'
        else:
            msg += 'Not visible exercise'
        flash(msg)
    kwargs = {'exercise': exercise, 'id': id, 'readonly': True}
    now = datetime.now()
    practice = False
    if seed is None:
        seed = user.random_seed
    elif now > exercise.close_date or user.is_admin:
        practice = True
        kwargs['readonly'] = False
    if seed is not None and seed != user.random_seed or user.is_admin:
        if now > exercise.close_date or user.is_admin:
            practice = True
            kwargs['readonly'] = False
    forms = list()
    status_list = list()
    points = list()
    ans_msgs = list()
    # Prepare lists for sorting questions by type
    optional_list = list()
    numerical_list = list()
    single_choice_list = list()
    no_answer_list = list()
    # Go through questions in an exercise and sort them by type
    for q in exercise.questions:
        answer = q.substitute_variables(seed)
        if q.no_answer:
            no_answer_list.append(q)
        elif type(answer) is float:
            numerical_list.append(q)
        elif len(answer) == 1:
            single_choice_list.append(q)
            #TODO: Following line unnecessary?
            q._options = [False for _ in range(5)]
        else:
            optional_list.append(q)
    # Now, when questions are sorted by type, create a dict
    # in which for every key is number of questions of the given type
    qlists = [single_choice_list, optional_list, numerical_list, 
            no_answer_list]
    qkeys = ['single', 'optional', 'numerical', 'no_answer']
    type_dict = dict()
    type_length = 0
    for i, qlist in enumerate(qlists):
        qlist.sort(key=lambda q: q.id)
        key = qkeys[i]
        if len(qlist) > 0:   # If there is at least one question of given type
            type_dict[type_length] = key
            type_length = type_length + len(qlist)
    # Merge lists of questions
    question_list = single_choice_list
    question_list.extend(optional_list)
    question_list.extend(numerical_list)
    question_list.extend(no_answer_list)
    # Prepare dictionary for output
    kwargs['type_dict'] = type_dict
    kwargs['question_list'] = question_list
    # Now we should have a dictionary of indices of first questions of a given
    # type. So for example if there is five questions with single answer and
    # then three answers with a numerical answer, the dict will look like
    # {'single':0, 'numerical':5} and in the question list, there will be five
    # questions with single answer and three with numerical answer
    flash_date = False
    # Now cycle through questions
    print("Questions info")
    for i, question in enumerate(question_list):
        print(i, question)
    for i, question in enumerate(question_list):
        print()
        print(f"{i}-th question {question}")
        print()
        ans_msg = ''
        status= ''
        if not practice:   # If the exercise is not for practise
            # Search if user already filled it
            sheet = Sheet.query.filter_by(
                    user_id = user.id,
                    exercise_id = exercise.id,
                    question_id = question.id).first()
            # If user already filled it inform him of last date of editation
            if sheet and sheet.edit_date and not flash_date:
                flash("Your answer was edited on " \
                      f"{sheet.edit_date.strftime('%Y/%m/%d, %H:%M')}")
                flash_date = True
        else:   # If the exercise is for practise, we do not save results
            sheet = False   # .. so no info about last editation
        # If the user have never done this exercise before, 
        # create a new sheet for them.
        # FIXME: If practice==True -> sheet == False --> new sheet is created
        if not sheet and not question.no_answer:
            sheet = Sheet(
                    user_id=user.id,
                    exercise_id=exercise.id,
                    question_id=question.id)
        if not question.no_answer:
            if sheet.point is not None:
                submitted = True
                if now < exercise.close_date:
                    kwargs['readonly'] = True
                if seed != user.random_seed:
                    practice = True
                    kwargs['readonly'] = False
        else:
            try:
                if last_edited:
                    last_edit = sheet.edit_date
                    flash(f'Last edit on {last_edit.strftime("%Y/%m/%d,%H:%M")}')
                    last_edited = False
            except:
                pass
        # Create a formular for a single question
        name = f'form-{i}'
        print(f"Form {name}")
        form = QuestionForm(
                exercise_id = exercise.id,
                question_id = question.id,
                user_id = user.id,
                prefix = name,
                obj = sheet)
        #form = QuestionForm()
        forms.append(form)
        if (now > exercise.open_date and now < exercise.close_date) \
                or practice and not submitted:
            print("1st condition")
            if not submitted:
                kwargs['readonly'] = False
            print(dir(form))
            print(f"form.validate_on_submit() == {form.validate_on_submit()}")
            print(f"question.no_answer == {question.no_answer}")
            if form.validate_on_submit() and not question.no_answer:
                print("2nd condition")
                if 'submit' in list(request.form.keys()):
                    submit = True
                    kwargs['readonly'] = True
                answer = question.substitute_variables(seed)
                if type(answer) is float:   # Question with float answer
                    #print("3rd condition")
                    # Error with saving and submitting is here
                    #print("REQUEST")
                    #print(dir(request))
                    #print()
                    #print("REQUEST.FORM")
                    #print(request.form)
                    #print(form)
                    #print(dir(form))
                    #print(form.number)
                    #print(form.exercise_id)
                    sheet.number = form.number.data
                    #print(f"For answer {answer} the float answer is {sheet.number}")
                elif len(answer) > 1:   # Multiple choice question
                    print("Multiple choice question")
                    sheet.option1 = form.option1.data
                    sheet.option2 = form.option2.data
                    sheet.option3 = form.option3.data
                    sheet.option4 = form.option4.data
                    sheet.option5 = form.option5.data
                else:
                    print("Last type of question")
                    rname = f"radio_{question.id}"
                    try:
                        print("Inside of try")
                        print(f"rname: {rname}")
                        print(f"request.form[{rname}]: {request.form[rname]}")
                        print(f"request.form[{rname}].split('_'): {request.form[rname].split('_')}")
                        ans = int(request.form[rname].split('_')[-1])
                    except:
                        print("Inside of expect")
                        ans = -1
                    print(f"Answer is {ans}")
                    question._options = [False for _ in range(5)]
                    sheet.option1 = False 
                    sheet.option2 = False 
                    sheet.option3 = False 
                    sheet.option4 = False 
                    sheet.option5 = False 
                    if ans == 0:
                        sheet.option1 = True
                    elif ans == 1:
                        sheet.option2 = True 
                    elif ans == 2:
                        sheet.option3 = True 
                    elif ans == 3:
                        sheet.option4 = True 
                    elif ans == 4:
                        sheet.option5 = True 
                    question._options[ans] = True
                # End of handling different types of questions with if blocks
                edit_time = datetime.now()
                sheet.edit_date = edit_time
                if not practice and not submitted:   # Handle submission of
                        # a test question
                    try:
                        db.session.add(sheet)
                        db.session.flush()
                    except:
                        error = "Answer can not be saved..., " +\
                                "please contact course administrator"
                    if sheet.id:
                        db.session.commit()
                        if not flashed:
                            if not submit:
                                flash('Answers has been saved on %s' % \
                                        edit_time.strftime(
                                        "%Y/%m/%d, %H:%M"))
                            else: 
                                flash('Your answer has been submitted')
                            flashed = True
                        if sheet.number is not None:
                            print(f"Your answer {sheet.number} was saved.")
                            ans_msg = f"Your answer {sheet.number} was saved."
                            status = 'text-info'
                        elif sheet.option1 or sheet.option2 or sheet.option3 \
                                or sheet.option4 or sheet.option5:
                            mask = np.array([
                                    sheet.option1,
                                    sheet.option2,
                                    sheet.option3,
                                    sheet.option4,
                                    sheet.option5])
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
                else:   # Handle submission of practice question.
                    if not flashed:
                        flash('Practice result will not be saved')
                        if submit:
                            flash('Results submitted')
                        flashed = True
            # FIXME: These two saving do not make much sense for now to me
            # necessary to render save check boxes
            elif seed == user.random_seed:
                try:
                    question._options[0] = sheet.option1
                    question._options[1] = sheet.option2
                    question._options[2] = sheet.option3
                    question._options[3] = sheet.option4
                    question._options[4] = sheet.option5
                except:
                    pass
        # necessary to render save check boxes
        elif seed == user.random_seed:
            try:
                question._options[0] = sheet.option1
                question._options[1] = sheet.option2
                question._options[2] = sheet.option3
                question._options[3] = sheet.option4
                question._options[4] = sheet.option5
            except:
                pass
        if now > exercise.close_date or practice or submit or submitted:
            if not question.no_answer:
                commit = True
                if practice or submitted:
                    commit = False
                point, status, ans_msg, error = evaluate(question, sheet, 
                        seed, commit)
                points.append(round(point, 3))
            if not practice:
                if now > exercise.close_date:
                    if not flashed:
                        flash('This exercise is already closed.')
                        flashed = True
                elif submit or submitted:
                    if not flashed:
                        flash('You have already submitted.')
                        flashed = True
            else:
                if not flashed:
                    flash('Practice results will not be saved.')
                    flashed = True
        if now < exercise.open_date:
           if not flashed:
               error = "Exercise not is opened yet, " \
                       "it is set to be open on " \
                       f"{exercise.open_date.strftime('%Y/%m/%d, %H:%M')}"
               flashed = True
        status_list.append(status)
        ans_msgs.append(ans_msg)
    print("End of cycle through questions")
    # End of cycle through questions
    # Prepare the output
    kwargs['status_list'] = status_list
    kwargs['points'] = points
    kwargs['ans_msgs'] = ans_msgs
    kwargs['forms'] = forms
    kwargs['error'] = error
    kwargs['seed'] = seed
    kwargs['practice'] = practice
    print("KWARGS")
    print(kwargs)
    return render_template('exercise/render.html', **kwargs)
