from teaching_site import db
import numpy as np

def evaluate(question, sheet, seed, commit=True):

    error = None
    point = 0.0
    status = 'text-danger'
    ans_msg = "You did not answer this question."
    answer =  question.evaluate(seed)
    if type(answer) is float:
        if sheet.number:
            tried = float(sheet.number)
            if answer == 0 and abs(tried) < 1E-3:
                point = 1.0
                ans_msg = "Your answer is correct!"
                status = 'text-success'
            elif answer != 0\
            and abs((tried - answer)/answer) < 0.1:
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

        if len(answer) > 1:

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
        else:
            if len(tried) > 0:
                if answer[0] == tried[0]:
                    point = 1.0
                    ans_msg = "Your answer is correct!"
                    status = 'text-success'
                else:
                    point = -1. / (n_options - 1)
                    ans_msg = "The correct answer is options: %d" \
                              % (answer[0] + 1)
                    ans_msg += ", but you chose options: %d" \
                               % (tried[0] + 1)

    ans_msg += " You've got %4.2f point." % (round(point, 3))

    sheet.point = point

    if commit:
        try:
            db.session.commit()
        except:
            error = "Evaluated results can not be saved, " +\
                    " please contact course administrator."
    return point, status, ans_msg, error
