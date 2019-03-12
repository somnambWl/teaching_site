#!/usr/bin/env python

import numpy as np

from app import db

def evaluate(question, sheet, seed, commit=True):
#    print()
#    print("Evaluation is running.")
    error = None
    point = 0.0
    status = 'text-danger'
    ans_msg = "You did not answer this question."
    # Get correct answer of the question with given seed.
#    print("Substituting variables")
    answer = question.substitute_variables(seed)
#    print()
#    print(f"Correct answer is {answer}")
#    print(f"Correct answer type is {type(answer)}")
    if type(answer) is float:
#        print("Answer type is float")
#        print(sheet.number)
        if sheet.number is not None:
#            print(f"Sheet number is {sheet.number}")
            tried = float(sheet.number)
            if answer == 0 and abs(tried) < 1E-3:
#                print("Answer is zero and correct")
                point = 1.0
                ans_msg = "Your answer is correct!"
                status = 'text-success'
            elif answer != 0 and abs((tried - answer)/answer) < 0.1:
#                print("Answer is not a zero and correct")
                point = 1.0
                ans_msg = "Your answer is correct!"
                status = 'text-success'
            else:
#                print("Answer is incorrect")
                ans_msg = f"The correct answer is {answer:.4E}," \
                        f" but you have entered {tried:.4E}."
#                print(f"Number of points: {point}")
        else:
            ans_msg = "You did not answer this question."
    else:
#        print("Answer is not float")
        answer = np.array(answer)
#        print(f"answer: {answer}")
        mask = np.array([sheet.option1, sheet.option2, sheet.option3, 
                sheet.option4, sheet.option5,])
#        print(f"mask: {mask}")
        for m in range(len(mask)):
            if mask[m] is None:
                mask[m] = False
        n_options = len(question.render(seed)[1])
#        print(f"n_options: {n_options}")
        choice = np.ma.masked_array(np.arange(1,6), ~mask)
#        print(f"choice: {choice}")
        tried = np.array([c for c in choice[:n_options] if c])-1
#        print(f"tried: {tried}")
        tried = tried.tolist()
        if len(answer) > 1:
            if not (sheet.option1 or sheet.option2 or sheet.option3 \
                    or sheet.option4 or sheet.option5):
                if not question.no_answer:   # If the question has an answer
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
                ans_msg, status = answer_for_multiple_choice(corrects,
                        n_options, answer, tried, point)
        else:
            if len(tried) > 0:
                if answer[0] == tried[0]:
                    point = 1.0
                    ans_msg = "Your answer is correct!"
                    status = 'text-success'
                else:
                    point = -1. / (n_options - 1)
                    ans_msg = f"The correct answer is options: {(answer[0] + 1)}"
                    ans_msg += f", but you chose options: {(tried[0] + 1)}"
#    print()
#    print(f"Final number of points: {point}")
#    print(f"Final number of points: {(round(point, 3)):4.2f}")
    ans_msg += f" You've got {(round(point, 3)):4.2f} point."
#    print(ans_msg)
    sheet.point = point
    if commit:
        try:
            db.session.commit()
        except:
            error = "Evaluated results can not be saved, " \
                    "please contact course administrator."
#    print()
    return point, status, ans_msg, error

def answer_for_multiple_choice(corrects, n_options, answer, tried, point):
    """
    Assemble a message for multiple choice question.

    Parameters
    ----------
    correct: int
        Number of correct answers
    n_options: int
        Number of options of the answer
    answer: list
        Correct answers as list. 
    tried: list
        Checked answers.
    point: float
        Number of points gained per the question.

    Returns
    -------
    ans_msg: str
        Answer message
    status: str
        Status
    """
    if corrects == n_options:
        ans_msg = "Your answer is correct!"
        status = 'text-success'
    else:
        if len(answer) == 1:
            ans_msg = f"The correct answer is option {(answer[0] + 1)}"
        elif len(answer) > 1:
            ans_msg = f"The correct answer are options {(answer[0] + 1)}"
            for j in answer[1:-2]:
                ans_msg += f", {(j + 1)}"
            ans_msg += f" and {answer[-1]}"
        if len(tried) == 1:
            ans_msg += f", but you chose option {(tried[0] + 1)}"
        elif len(tried) > 1:
            ans_msg += f", but you chose options {(tried[0] + 1)}"
            for j in tried[1:-2]:
                ans_msg += f", {(j + 1)}" 
            ans_msg += f" and {tried[-1]}"
        ans_msg += '.'
        status = 'text-warning'
        if point <= 0:
            status = 'text-danger'
    return ans_msg, status
