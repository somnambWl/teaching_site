
from app import app, db

from datetime import datetime

import pandas as pd

from flask_table import Table, Col, create_table

from sqlalchemy import func

from app.models.exercise import Exercise, Sheet, Question
from app.models.user import User

def create_summary_table():
    """
    Create a summary table (DataFrame) from database for admin's home.

    Returns
    -------
    pandas.DataFrame:
        Summary table
    """
    sql = db.session.query(User.fullname, Exercise.name,
            func.sum(Sheet.point)).filter(Sheet.user_id==User.id)\
            .filter(Sheet.exercise_id==Exercise.id)\
            .filter(User.enrolled==True)\
            .filter(Exercise.scored==True)\
            .group_by(User.fullname, Exercise.name)
    #print("SQL statement")
    #print(sql.statement)
    #print("SQL data")
    #print(sql.all())
    try:
        df = pd.read_sql(sql.statement, db.session.bind)
        df = df.pivot_table(values='sum_1', index="fullname", columns="name")
        df.index.name = None
        df.columns.name = None
        df["Total"] = df[list(df.columns)].sum(axis=1)
        return df
    except:
        return None
