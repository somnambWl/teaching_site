
from app import app, db

from datetime import datetime

import pandas as pd

from flask_table import Table, Col, create_table

from sqlalchemy import func

from app.models.exercise import Exercise, Sheet, Question
from app.models.user import User

def create_summary_table():
    sql = db.session.query(User.fullname, Exercise.name,
            func.sum(Sheet.point)).filter(User.enrolled)\
            .group_by(Exercise.name)
    try:
        df = pd.read_sql(sql.statement, db.session.bind)
        df = df.pivot_table(values='sum_1', index="fullname", columns="name")
        df.index.name = None
        df.columns.name = None
        df["Total"] = df[list(df.columns)].sum(axis=1)
        return df
    except:
        return None
