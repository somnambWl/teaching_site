def _get_answers_from_str(answer_str):
    """
    get answer list for each subquestion from answer_str
    answer_str is of the format (e.g.): r"$m$;0.387;True",
    where allowed answers are separated by semicolon

    input:               output:
    r"$m$;0.387;True" -> [r"$m$", 0.387, True]
    """
    pass

def _get_variables_from_db(db_query):
    pass

def build_question(db_query_list):

    """
    Interface for database storage. 
    Reconstruct Question from database entry
    """

    name = db_query_list[0].name
    body_list = [q.body for q in db_query_list]
    answers_list = [_get_answers_from_str(q.answer) \
                    for q in db_query_list]
    variables_list = [_get_variables_from_db(q) \
                      for q in db_query_list]

    return name, body_list, answers_list, variables_list

class Question(object):

    """
    Question class is used to render question and evaluate answer.
    It will be constructed on demand.
    The data structure is strongly coupled with SQLAlchemy model.

    Question class:
        body_list: List of question text,
                   each entry for each version

        anwers_list: List of correct answers, 
                     each entry is a list of 
                     all possible correct answers, 
                     Each entry of the sublist is string, 
                     either exicutable or latex text

        variables_list: List of variables, 
                        each entry is the list 
                        of all variables for each version
                        Each entry of the sublist 
                        is a list of all variables
                        Each entry of the subsublist is 
                        a dictionary of:
                        type, name, range, condition

        The length of each list is the number of subversions
        for each question

        The conditions above are asserted
    """

    def __init__(self, 
                 name,
                 body_list, 
                 answers_list, 
                 variables_list
                 ):
        assert type(body_list) is list
        assert type(body_list[0]) is str
        assert type(answers_list) is list
        assert type(answers_list[0]) is list
        assert type(answers_list[0][0]) is str
        assert type(variables_list) is list
        assert type(variables_list[0]) is list
        assert type(variables_list[0][0]) is dict
        assert len(body_list) == len(answers_list) == len(variables_list)

        self.name = name
        self.body_list = body_list
        self.answers_list = answers_list
        self.variables_list = variables_list

    def __repr__(self):
        return self.name
