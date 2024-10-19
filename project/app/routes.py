from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
import os
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from project.utils.auth import authenticate, create_user, validate_email, update_password
from project.extensions.dependencies import db
from project.models.users import User, ProfilePicture
from project.models.products import Product, ProductVariation, ProductVariationImage

app = Blueprint('app', __name__, template_folder='templates', static_folder='static', static_url_path='/')

UPLOADS_FOLDER = os.path.join(app.static_folder, 'app/uploads/')
STATIC_URL_PATH = f'/{app.name}/uploads/'
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
        first_name = request.form.get('fullname').split()[0] if len(request.form.get('fullname').split()) > 0 else ''
        last_name = request.form.get('fullname').split()[1] if len(request.form.get('fullname').split()) > 1 else ''
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('cpassword')
        terms = True if request.form.get('terms') else False

        if terms:
            print('passed')
            user, error = create_user(first_name=first_name, last_name=last_name, email=email, password=password, confirm_password=confirm_password)
            flash(error)
            if user is not None:
                login_user(user=user)
                return redirect(url_for('app.index'))
        else:
            flash({'terms': 'You must agree to the terms and conditions'})


        return render_template('app/signup.html')

@app.route('/settings', methods=['GET', 'PUT'])
@login_required
def settings():
    if request.method == 'PUT':
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

@app.route('/update_profile_image', methods=['POST'])
def update_profile_image():
    if request.method == 'POST':
        data = request.form
        if data.get('action') == 'picture-form':
            file = request.files.get('profile-picture')
            print(file)
            if file.filename == '':
                jsonify({'status': 'error', 'message': 'No selected file'})
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOADS_FOLDER, f'profileimg/{filename}')
                relative_url = STATIC_URL_PATH + f'profileimg/{filename}'
                file.save(file_path)

                # Clear all previous profile pictures and save new one
                current_user.profile_picture.clear()
                pfp = ProfilePicture(url=relative_url, user=current_user)
                db.session.add(pfp)
                db.session.commit()
                return jsonify({'status': 'success', 'image_url': current_user.get_profile_picture_url()})

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('app.index'))

@app.route('/account')
def account():
    return render_template('app/account.html')

@app.route('/billing')
def billing():
    return render_template('app/billing.html')

@app.route('/payment')
def payment():
    return render_template('app/payment.html')

@app.route('/social')
def social():
    return render_template('app/social.html')

@app.route('/shop')
def shop():
    products = ''
    products = Product.query.all()  # Get all products

    # For each product, choose a default or first variation to display
    product_data = []
    for product in products:
        if product.variations:  # Ensure the product has variations
            primary_variation = product.variations[0]  # Default to the first variation
            primary_image = primary_variation.images[0].image_url if primary_variation.images else '/static/default_image.jpg'

            product_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': primary_variation.price,
                'variation': f'{primary_variation.color} {primary_variation.size}',
                'image_url': primary_image
            })
    return render_template('app/shop.html', products=product_data)

@app.route('/cart')
def cart():
    return render_template('app/cart.html')

@app.route('/checkout')
def checkout():
    return render_template('app/checkout.html')

@app.route('/product_detail/<int:product_id>')
def product_details(product_id):
    # Fetch the product by ID
    product = Product.query.get_or_404(product_id)

    # Prepare data for product variations and images
    variations = []
    for variation in product.variations:
        images = [image.image_url for image in variation.images]
        variations.append({
            'id': variation.id,
            'color': variation.color,
            'size': variation.size,
            'price': variation.price,
            'images': images
        })

    product_data = {
        'name': product.name,
        'description': product.description,
        'base_price': product.price,
        'variations': variations
    }
    # print(product_data)

    return render_template('app/product_detail.html', product=product_data)