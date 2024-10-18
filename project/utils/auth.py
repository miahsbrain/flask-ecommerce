from project.extensions.dependencies import db, bcrypt
from project.models.users import User
from sqlalchemy import exists
import re

def authenticate(email, password):
    ''' User authentication for login '''
    user = User.query.filter(User.email==email).first()

    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
            return (user, None)
        else:
            return (None,  {'password': "Incorrect password", 'cat': 'danger'})
    else:
        return (None,  {'email': "Email doesn't exist", 'cat': 'danger'})

def validate_email(email):
    ''' Email validation with regex '''
    pattern = re.compile("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\\.[A-Z|a-z]{2,})+")
    if not re.match(pattern, email):
        return (None, 'Please enter a valid email address')
    return (email, None)

def validate_password(password):
    ''' Password validation with regex '''
    if len(password) < 6 :
        return (None, 'Password too short')
    l_pattern = re.compile("^(?=.*[a-z])[A-Za-z0-9@#$!%*?&]{6,20}$")
    if not re.match(l_pattern, password):
        return (None, 'Password must contain a lowercase letter')
    u_pattern = re.compile("^(?=.*[A-Z])[A-Za-z0-9@$#!%*?&]{6,20}$")
    if not re.match(u_pattern, password):
        return (None, 'Pasword must contain an uppercase letter')
    d_pattern = re.compile("^(?=.*[0-9])[A-Za-z0-9@$#!%*?&]{6,20}$")
    if not re.match(d_pattern, password):
        return (None, 'Pasword must contain a number')
    s_pattern = re.compile("^(?=.*[@#$!%*?&])[A-Za-z0-9@$#!%*?&]{6,20}$")
    if not re.match(s_pattern, password):
        return (None, 'Pasword must contain a special character')
    return (password, None)

def create_user(first_name, last_name, email, password, confirm_password, is_admin=False):
    '''
    Function to validate user and create user
    '''
    if not first_name:
        return (None, {'f_name':'You are missing your first name', 'cat': 'danger'})
    if not last_name:
        return (None, {'l_name':'You are missing your last name', 'cat': 'danger'})
    if not email:
        return (None, {'email':'You are missing your email address','cat': 'danger'})
    if not password:
        return (None, {'password':'Please choose a password', 'cat': 'danger'})
    if not confirm_password:
        return (None, {'c_password':'Please confirm your password', 'cat': 'danger'})
    
    # Validate email
    if len(list(User.query.filter(User.email==email))) > 0:
        return (None, {'email':'Email already exists', 'cat': 'danger'})
    email, error = validate_email(email=email)
    if email is None:
        return (None, {'email':error})
    
    # Validate password
    password, error = validate_password(password=password)
    if password is None:
        return (None, {'password':error, 'cat': 'danger'})
    if password != confirm_password:
        return (None, {'c_password':'Passwords must match', 'cat': 'danger'})
    password = bcrypt.generate_password_hash(password)
    user = User(first_name=first_name, last_name=last_name, email=email, password=password, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return (user, None)

def update_password(user, password, confirm_password):
    # Validate password
    password, error = validate_password(password=password)
    if password is None:
        return {'password':error, 'cat': 'danger'}
    if password != confirm_password:
        return {'c_password':'Passwords must match', 'cat': 'danger'}
    user.password = bcrypt.generate_password_hash(password)
    db.session.commit()
    return {'password': 'Password has be updated successfully', 'cat': 'success'}