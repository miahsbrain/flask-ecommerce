from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
import os
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from project.utils.auth import authenticate, create_user, validate_email, update_password
from project.extensions.dependencies import db
from project.models.users import ProfilePicture
from project.models.products import Product, ProductVariation, Cart, CartItem, Order, OrderItem, ShippingAddress, Payment, Color, Brand, Size
from functools import reduce
import requests

app = Blueprint('app', __name__, template_folder='templates', static_folder='static', static_url_path='/')

PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
UPLOADS_FOLDER = os.path.join(app.static_folder, 'app/uploads/')
STATIC_URL_PATH = f'/{app.name}/uploads/'
if not os.path.exists(UPLOADS_FOLDER): os.mkdir(UPLOADS_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    items = []
    if session.get('cart'):
        items = session.get('cart')
        session.pop('cart')
    return render_template('app/index.html', init_cart=items)

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
            cart = Cart.get_or_create(user)
            items = [{
                'id': item.id,
                'product_id': item.product_variation.product.id,
                'variation_id': item.variation_id,
                'name': item.product_variation.product.name,
                'price': round(float(item.product_variation.price), 2),
                'size': item.product_variation.size,
                'color': item.product_variation.color,
                'quantity': item.quantity,
                'image': item.product_variation.images[0].image_url,
                'total': round(float(item.product_variation.price * item.quantity), 2)
            } for item in cart.items]
            session['cart'] = items

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

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        data = request.form
        print(data.get('fname'))
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
                if current_user.profile_picture:
                    current_user.profile_picture.clear()
                pfp = ProfilePicture(url=relative_url, user=current_user)
                db.session.add(pfp)
                db.session.commit()
                flash({'profile_picture':'Profile picture updated successfully!', 'cat': 'success'})
                return render_template('app/settings.html')
        elif data.get('action') == 'personal-info-form':
            print('triggered')
            if data.get('fname'):
                current_user.first_name = str(data.get('fname'))
                db.session.commit()
                flash({'f_name':'First name updated successfully', 'cat': 'success'})
            if data.get('lname'):
                current_user.last_name = str(data.get('lname'))
                db.session.commit()
                flash({'l_name':'Last name updated successfully', 'cat': 'success'})
            if data.get('phone'):
                current_user.phone = int(data.get('phone'))
                db.session.commit()
                flash({'phone':'Phone number updated successfully', 'cat': 'success'})
            if data.get('email'):
                email, error = validate_email(email=str(data.get('email')))
                if email is not None:
                    current_user.email = email
                    db.session.commit()
                    flash({'email':'Email address updated successfully', 'cat': 'success'})
                else:
                    flash({'email':error, 'cat': 'danger'})
        elif data.get('action') == 'security-info-form':
            if current_user.check_password(data.get('oldpassword')):
                response = update_password(user=current_user, password=data.get('newpassword'), confirm_password=data.get('confirmpassword'))
                flash(response)
            else:
                flash({'oldpassword':'Invalid password for current user', 'cat': 'danger'})

    return render_template('app/settings.html')

@app.route('/update_profile_image', methods=['PUT'])
def update_profile_image():
    if request.method == 'PUT':
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
                if current_user.profile_picture:
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
    all_orders = []
    for order in current_user.orders:
        if len(all_orders) < 3:
            all_orders.append({
                'id': order.id,
                'date': order.created_at.strftime('%B %d, %Y'),
                'status': order.status,
                'total': order.total_price,
                'no_of_items': reduce(lambda total, item: total + item, [items.quantity for items in order.items])
            })

    return render_template('app/account.html', orders=all_orders)

@app.route('/billing')
def billing():
    return render_template('app/billing.html')

@app.route('/payment')
def payment():
    all_payments = []
    for payment in current_user.payments:
        all_payments.append({
            'order_id': payment.order_id,
            'transaction_id': payment.transaction_id,
            'date': payment.created_at.strftime('%B %d, %Y'),
            'payment_status': payment.payment_status,
            'amount_paid': payment.amount_paid
        })
    return render_template('app/payment.html', payments=all_payments)

@app.route('/orders')
def complete_checkout():
    return jsonify({'order': 'success'})

@app.route('/social')
def social():
    return render_template('app/social.html')

@app.route('/shop')
def shop():
    # Get the filter values from the request args
    name_filter = request.args.get('s', '')
    color_filter = request.args.get('color', '')
    brand_filter = request.args.get('brand', '')
    size_filter = request.args.get('size', '')

    # Get page from query params, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 2  # Number of products per page

    # Start with a base query
    query = Product.query

    # Join product variations if color, size filters or brand filters
    if color_filter or size_filter or brand_filter:
        query = query.join(ProductVariation)

    # Apply filters if any
    if color_filter:
        query = query.join(Color).filter(Color._color.ilike(color_filter))
    if brand_filter:
        query = query.join(Brand).filter(Brand.brand.ilike(brand_filter))
    if size_filter:
        query = query.join(Size).filter(Size._size==size_filter)
    if name_filter:
        query = query.filter(Product.name.ilike(f"%{name_filter}%"))

    # Execute the query
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    # Paginate the query
    total_products = query.count()
    # Calculate the number of total pages
    total_pages = round(total_products / per_page)
    info = f'Showing {((page - 1) * per_page)}-{(page * per_page)} of {total_products} items'
    # print(info)

    # print(products)
    # print(total_pages)
    # print(total_products)


    # For each product, choose a default or first variation to display
    product_data = []
    colors = []
    sizes = []
    brands = []

    # Gets all the colors to send
    for color in Color.query.all():
        colors.append({
            'color': color.color,
            'hex': color.hex
        })
    # Gets all the sizes to send
    for size in Size.query.all():
        sizes.append(size.size)
    for brand in Brand.query.all():
        brands.append(brand.brand)


    for product in products:
        if product.variations:  # Ensure the product has variations
            primary_variation = product.variations[0]  # Default to the first variation
            primary_image = primary_variation.images[0].image_url if primary_variation.images else '/static/default_image.jpg'

            product_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': primary_variation.price,
                'sale': primary_variation.sale,
                'featured': primary_variation.featured,
                'variation_id': primary_variation.id,
                'variation': f'{primary_variation.color} {primary_variation.size}',
                'image_url': primary_image
            })

    return render_template('app/shop.html', products=product_data, colors=colors, sizes=sizes, brands=brands, page=page, total_pages=total_pages, info=info)


@app.route('/product_detail/<int:product_id>')
def product_details(product_id):
    # Fetch the product by ID
    product = Product.query.get_or_404(product_id)

    # Prepare data for product variations and images
    variations = []
    for variation in product.variations:
        images = [image.image_url for image in variation.images]
        variations.append({
            'variation_id': variation.id,
            'color': {'color':variation.color.color, 'hex':variation.color.hex},
            'size': variation.size.size,
            'price': variation.price,
            'sale': variation.sale,
            'images': images,
        })


    product_data = {
        'id': product_id,
        'name': product.name,
        'description': product.description,
        'overview': product.overview,
        'highlights': [highlight.highlight for highlight in product.highlights],
        'brand': product.brand.brand,
        'variations': variations
    }

    return render_template('app/product_detail.html', product=product_data)

@app.route('/cart')
@login_required
def cart():
    cart = Cart.get_or_create(current_user)
    
    items = [{
        'id': item.id,
        'product_id': item.product_variation.product.id,
        'variation_id': item.variation_id,
        'name': item.product_variation.product.name,
        'price': round(float(item.product_variation.price), 2),
        'size': item.product_variation.size.size,
        'color': {'color':item.product_variation.color.color, 'hex':item.product_variation.color.hex},
        'quantity': item.quantity,
        'image': item.product_variation.images[0].image_url,
        'total': round(float(item.product_variation.price * item.quantity), 2)
    } for item in cart.items]
    
    return render_template('app/cart.html', cart=items)

@app.route('/validate_cart', methods=['GET', 'POST'])
def validate_cart():
    cart = Cart.get_or_create(current_user)
    
    items = [{
        'id': item.id,
        'product_id': item.product_variation.product.id,
        'variation_id': item.variation_id,
        'name': item.product_variation.product.name,
        'price': round(float(item.product_variation.price), 2),
        'size': item.product_variation.size.size,
        'color': {'color':item.product_variation.color.color, 'hex':item.product_variation.color.hex},
        'quantity': item.quantity,
        'image': item.product_variation.images[0].image_url,
        'total': round(float(item.product_variation.price * item.quantity), 2)
    } for item in cart.items]
    
    return jsonify({'cart': items})

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    if request.method == 'POST':
        data = request.form

        cart = Cart.get_or_create(current_user)

        # Check if item already exists in cart
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            variation_id=data['variation_id'],
            product_id=data['product_id']
        ).first()
        
        if cart_item:
            cart_item.quantity += int(data['quantity'])
        else:
            cart_item = CartItem(
                product_id=data['product_id'],
                variation_id=data['variation_id'],
                quantity=data['quantity'],
                cart_id = cart.id
            )
            db.session.add(cart_item)
        db.session.commit()

        items = [{
            'id': item.id,
            'product_id': item.product_variation.product.id,
            'variation_id': item.variation_id,
            'name': item.product_variation.product.name,
            'price': round(float(item.product_variation.price), 2),
            'size': item.product_variation.size.size,
            'color': {'color':item.product_variation.color.color, 'hex':item.product_variation.color.hex},
            'quantity': item.quantity,
            'image': item.product_variation.images[0].image_url,
            'total': round(float(item.product_variation.price * item.quantity), 2)
        } for item in cart.items]
        
        return jsonify({'cart': items})

@app.route('/update_cart', methods=['GET', 'PUT'])
def update_cart():
    data = request.form
    cart = Cart.get_or_create(current_user)

    if request.method == 'PUT':
        cart_item = CartItem.query.filter_by(
                cart_id=cart.id,
                product_id=data['product_id'],
                variation_id=data['variation_id']
            ).first()

        if cart_item:
            cart_item.quantity = int(data['quantity'])

            if cart_item.quantity <= 0:
                db.session.delete(cart_item)

        db.session.commit()

    items = [{
        'id': item.id,
        'product_id': item.product_variation.product.id,
        'variation_id': item.variation_id,
        'name': item.product_variation.product.name,
        'price': round(float(item.product_variation.price), 2),
        'size': item.product_variation.size.size,
        'color': {'color':item.product_variation.color.color, 'hex':item.product_variation.color.hex},
        'quantity': item.quantity,
        'image': item.product_variation.images[0].image_url,
        'total': round(float(item.product_variation.price * item.quantity), 2)
    } for item in cart.items]
    
    return jsonify({'cart': items})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = Cart.get_or_create(current_user)
    items = [{
        'id': item.id,
        'product_id': item.product_variation.product.id,
        'variation_id': item.variation_id,
        'name': item.product_variation.product.name,
        'price': round(float(item.product_variation.price), 2),
        'size': item.product_variation.size.size,
        'color': {'color':item.product_variation.color.color, 'hex':item.product_variation.color.hex},
        'quantity': item.quantity,
        'image': item.product_variation.images[0].image_url,
        'total': round(float(item.product_variation.price * item.quantity), 2)
    } for item in cart.items]

    if request.method == 'GET':
        return render_template('app/checkout.html', checkout_items=items, public_key=PAYSTACK_PUBLIC_KEY)

    elif request.method == 'POST':
        data = request.form
        total_price = round(reduce(lambda total, item: total+item, [(item.quantity * item.product_variation.price) for item in cart.items]), 2)
        reference = data['reference']

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        # Verify the payment with Paystack
        response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)

        if response.status_code == 200:
            payment_data = response.json()['data']
            
            # Validate the amount (paystack returns amount in kobo for NGN or cents for USD)
            paid_amount = payment_data['amount']
            currency = payment_data['currency']

            if currency == "USD":
                expected_amount_in_cents = round(float(total_price * 100), 2)  # Convert USD to cents
            else:
                expected_amount_in_cents = round(float(total_price * 100), 2)  # Convert NGN or other currencies

            if paid_amount == expected_amount_in_cents:
                # Payment successful, proceed with creating the order

                # SUCCESSFULLY CREATED NEW SHIPPING ADDRESS AND ORDER
                shipping_address = ShippingAddress(user=current_user,
                                                first_name=data['firstname'],
                                                last_name=data['lastname'],
                                                email=data['email'],
                                                phone=data['phone'],
                                                address_line_1=data['address'],
                                                address_line_2=data['address2'],
                                                city=data['city'],
                                                state=data['state'],
                                                zip_code=data['zipcode'],
                                                country=data['country']
                                                )
                total_price = round(reduce(lambda total, item: total+item, [(item.quantity * item.product_variation.price) for item in cart.items]), 2)
                order = Order(user=current_user, shipping_address=shipping_address, total_price=total_price)
                payment = Payment(user=current_user, order=order, transaction_id=reference, email=data['email'], amount_paid=paid_amount, currency=currency, payment_status='Paid')
                
                db.session.add(shipping_address)
                db.session.add(order)
                db.session.add(payment)

                # print(shipping_address)
                # print(order)

                for item in cart.items:
                    order_item = OrderItem(order=order,
                                        product_id=item.product_id,
                                        variation_id=item.variation_id,
                                        quantity=item.quantity,
                                        price_at_purchase=item.product_variation.price,
                                        total_price=round(float(item.product_variation.product.price * item.quantity), 2)
                                        )
                    db.session.add(order_item)

                
                print(order.items)
                print(order.total_price)
                print(payment)
                CartItem.query.filter_by(cart_id=cart.id).delete()
                db.session.commit()

                return jsonify({"status": "success", "message": "Payment verified and order created", "order_id": order.id})
            else:
                return jsonify({"status": "failed", "message": "Payment amount mismatch"}), 400
        else:
            return jsonify({"status": "failed", "message": "Payment verification failed"}), 400

