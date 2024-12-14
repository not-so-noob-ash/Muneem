from Muneem import app, db
from Muneem.models import User
from werkzeug.security import generate_password_hash  # to hash the password

# Drop all tables and then create them again within the app context
with app.app_context():
    # db.drop_all()  # Drops all tables
    # db.create_all()  # Creates all tables again

    # Create a new user
    hashed_password = generate_password_hash('your_password_here', method='sha256')
    new_user = User(
        username='user3',
        email_address='testuser3@example.com',
        password_hash=hashed_password,
        budget=1000.0,  # Example budget
        preffered_currency='USD'
    )

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    print("All tables dropped, created successfully, and a new user added!")
