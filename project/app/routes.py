from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import os
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from project.utils.auth import authenticate, create_user, validate_email, update_password
from project.extensions.dependencies import db
from project.models.users import User, ProfilePicture

app = Blueprint('app', __name__, template_folder='templates', static_folder='static', static_url_path='/')

UPLOADS_FOLDER = os.path.join(app.static_folder, 'app/uploads')
STATIC_URL_PATH = f'/{app.name}/static/app/uploads/'
if not os.path.exists(UPLOADS_FOLDER): os.mkdir(UPLOADS_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('app/index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('app.index'))
        return render_template('app/signin.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember-me') else False
        user, error = authenticate(email=email, password=password)
        flash(error)
        if user is not None:
            login_user(user=user, remember=remember)
            return redirect(url_for('app.index'))
        return render_template('app/signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('app/signup.html')
    elif request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('cpassword')

        user, error = create_user(first_name=first_name, last_name=last_name, email=email, password=password, confirm_password=confirm_password)
        flash(error)
        if user is not None:
            login_user(user=user)
            return redirect(url_for('app.index'))

        return render_template('app/signup.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    data = request.form
    if data.get('action') == 'picture-form':
        file = request.files.get('profile-picture')
        if file.filename == '':
            flash({'profile_picture':'No selected file', 'cat': 'danger'})
            return render_template('app/settings.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOADS_FOLDER, filename)
            relative_url = STATIC_URL_PATH + filename
            file.save(file_path)

            # Clear all previous profile pictures and save new one
            current_user.profile_picture.clear()
            pfp = ProfilePicture(url=relative_url, user=current_user)
            db.session.add(pfp)
            db.session.commit()
            flash({'profile_picture':'Profile picture updated successfully!', 'cat': 'success'})
            return render_template('app/settings.html')
        pass
    elif data.get('action') == 'info-form':
        if data.get('fname'):
            current_user.first_name = str(data.get('fname'))
            db.session.commit()
            flash({'f_name':'First name updated successfully', 'cat': 'success'})
        if data.get('lname'):
            current_user.last_name = str(data.get('lname'))
            db.session.commit()
            flash({'l_name':'Last name updated successfully', 'cat': 'success'})
        if data.get('email'):
            email, error = validate_email(email=str(data.get('email')))
            if email is not None:
                current_user.email = email
                db.session.commit()
                flash({'email':'Email address updated successfully', 'cat': 'success'})
            else:
                flash({'email':error, 'cat': 'danger'})
    elif data.get('action') == 'password-form':
        response = update_password(user=current_user, password=data.get('password'), confirm_password=data.get('cpassword'))
        flash(response)
    return render_template('app/settings.html')

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('core.index'))

@app.route('/newpost')
def newpost():
    return render_template('app/newpost.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    data = request.get_json()
    url_one = data.get('url_one')
    if not url_one:
        url_one = 'https://quotes.toscrape.com/random'
    urls = [url_one, ]
    return Response(task_manager.process_request(urls=urls), content_type='text/event-stream')