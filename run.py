from app import app, db
from app.models.user import User
from app.data.initialize import initialize_admin, initialize_units, \
        initialize_unit_categories
#        initialize_variables, initialize_questions, initialize_exercises


if __name__ == '__main__':
    db.create_all()   # Create the database
    db.session.commit()   # Confirm the creation
    initialize_admin()
    initialize_unit_categories("./app/data/unit_categories.csv")
    initialize_units("./app/data/units.csv")
    #initialize_variables()
    #initialize_questions()
    #initialize_exercises()
    # Run the app
    app.run(host="0.0.0.0")
