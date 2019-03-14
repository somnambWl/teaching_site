import pandas as pd

from app import app, db

from app.models.user import User
from app.models.question import UnitCategory, Unit

def initialize_admin():
    # Create admin
    old_admin = User.query.filter_by(is_admin=True).first()
    if old_admin:
        print("There already is one admin.")
    else:
        admin = User(
                username = "admin",
                email = "somnambWl@gmail.com",
                password_tmp = 'admin',
                enrolled = False,
                validated = True,
                is_admin = True)
        try:
            db.session.add(admin)
            db.session.commit()
        except:
            print("Admin can not be added.")

def initialize_unit_categories(filename):
    """
    Initialize UnitCategory from file
    """
    try:
        data = pd.read_csv(filename, delimiter="\t", na_filter=False)
    except:
        pass
#        print("Error while initializing unit categories")
    for index, row in data.iterrows():
        try:
            db.session.add(UnitCategory(*row))
            db.session.commit()
        except:
            pass
#            print(f"Error with {row}")
#            print()

def initialize_units(filename):
    """
    Initialize Unit from file
    """
    try:
        data = pd.read_csv(filename, delimiter="\t", na_filter=False)
    except:
        prass
#        print("Error while initializing units")
    for index, row in data.iterrows():
        try:                             
            db.session.add(Unit(*row))
            db.session.commit()         
        except:                        
            pass
#            print(f"Error with {row}")
#            print()
