from project.extensions import db, bcrypt
from project.models.users import User
from project import create_app

def create_user():
    first_name = input('Enter your first name: ')
    last_name = input('Enter your last name: ')
    email = input('Enter your email: ')
    password = input('Enter your password: ')
    hashed_password = bcrypt.generate_password_hash(password)
    user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
    with create_app().app_context():
        db.session.add(user)
        db.session.commit()

def createsuper_user():
    first_name = input('Enter your first name: ')
    last_name = input('Enter your last name: ')
    email = input('Enter your email: ')
    password = input('Enter your password: ')
    hashed_password = bcrypt.generate_password_hash(password)
    user = User(first_name=first_name, last_name=last_name, email=email, is_admin=True, password=hashed_password)
    with create_app().app_context():
        db.session.add(user)
        db.session.commit()

is_admin = input('[0] for normal user and [1] for super user: ')

is_admin = int(is_admin)
if is_admin == 0:
    create_user()
elif is_admin == 1:
    createsuper_user()