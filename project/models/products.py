from project.models.base import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Float, DateTime
from datetime import datetime, timezone
from project.extensions.dependencies import db
from sqlalchemy.orm import relationship

class Product(BaseModel):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    overview = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    brand =  relationship('Brand', uselist=False, lazy=True)
    highlight =  relationship('Highlight', uselist=True, lazy=True, cascade='all, delete-orphan')
    user_id = Column(Integer, ForeignKey('users.uid', name='fk_products_user'))
    
    # Relationship to ProductVariation
    variations = relationship('ProductVariation', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductVariation(BaseModel):
    __tablename__ = 'product_variations'

    id = Column(Integer, primary_key=True)
    color = relationship('Color', uselist=False, lazy=True)  # Color variation
    _size = Column(String(50), nullable=True)  # Size variation, optional
    price = Column(Float, nullable=False)  # Price specific to this variation
    sale = Column(Float, nullable=True)
    featured = Column(Boolean, nullable=True, default=False)
    stock = Column(Integer, nullable=False, default=1)  # Stock for this variation

    product_id = Column(Integer, ForeignKey('products.id', name='fk_product_variations_product'), nullable=False)

    # Relationship to ProductVariationImage
    images = relationship('ProductVariationImage', backref='variation', lazy=True)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value.upper()  # Ensures the brand is always uppercase

    def __repr__(self):
        return f'<ProductVariation {self.color} {self.size}>'
        

class Color(db.Model):
    __tablename__ = 'colors'

    id = Column(Integer, primary_key=True)
    variation_id = Column(Integer, ForeignKey('product_variations.id', name='fk_colors_product_variation'))
    _color = Column(String(50), nullable=True, default='Gray')
    _hex = color = Column(String(50), nullable=True, default='#808080')

    @classmethod
    def get_or_create(cls, color_name):
        color = cls.query.filter(cls._color.ilike(color_name)).first()

        if color:
            return color
        else:
            new_color = cls(color=color_name)
            db.session.add(new_color)
            db.session.commit()
            return new_color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value.lower()  # Ensures the brand is always lowercase

    @property
    def hex(self):
        return self._hex

    @hex.setter
    def hex(self, value):
        self._hex = value.upper()  # Ensures the brand is always uppercase

class Brand(db.Model):
    __tablename__ = 'brands'

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('products.id', name='fk_brands_product'))
    brand = Column(String(50), nullable=True)

    @classmethod
    def get_or_create(cls, brand_name):
        brand = cls.query.filter(cls.brand.ilike(brand_name)).first()

        if brand:
            return brand
        else:
            new_brand = cls(brand=brand_name)
            db.session.add(new_brand)
            db.session.commit()
            return new_brand

class Highlight(db.Model):
    __tablename__ = 'highlights'

    id = Column(Integer, primary_key=True)
    highlight_id = Column(Integer, ForeignKey('products.id', name='fk_highlights_product'))
    highlight = Column(String(50), nullable=True)

class ProductVariationImage(db.Model):
    __tablename__ = 'product_variation_images'

    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)  # URL or path to the image
    variation_id = Column(Integer, ForeignKey('product_variations.id', name='fk_product_variation_images_product_variation'), nullable=False)

    def __repr__(self):
        return f'<ProductVariationImage {self.image_url}>'

class Cart(db.Model):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.uid', name='fk_cart_items_user'), nullable=False)
    items = relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    @classmethod
    def get_or_create(cls, user):
        """Get existing cart or create new one for user"""
        if user.cart is None:
            cart = cls(user_id=user.uid)
            db.session.add(cart)
            db.session.commit()
        return user.cart

    def __repr__(self):
        return f"<Cart {self.id} - items: {self.items}>"


# Shopping Cart model to store user's cart items before checkout
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id', name='fk_cart_items_product'), nullable=False)
    cart_id = Column(Integer, ForeignKey('carts.id', name='fk_cart_items_cart'), nullable=False)
    quantity = Column(Integer, default=1)
    variation_id = Column(Integer, ForeignKey('product_variations.id', name='fk_cart_items_variation'), nullable=False)  # Store selected variation
    product = relationship('Product', uselist=False)
    product_variation = relationship('ProductVariation', uselist=False)

    def __repr__(self):
        return f"<CartItem {self.product_id} - Quantity: {self.quantity}>"
    

# Order model to store information about the order
class Order(BaseModel):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.uid'), nullable=False)
    total_price = Column(Float, nullable=False, default=0)
    status = Column(String(50), default="Processing")  # Processing, Confirmed, Shipped, Delivered

    # One order can have multiple items
    items = relationship('OrderItem', backref='order', lazy=True)

    # Shipping address for the order
    shipping_address_id = Column(Integer, ForeignKey('shipping_addresses.id'), nullable=False)
    shipping_address = relationship('ShippingAddress', uselist=False, lazy=True)

    def __repr__(self):
        return f"<Order {self.id} - Status: {self.status}>"

# Items within an order
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    variation_id = Column(Integer, ForeignKey('product_variations.id'), nullable=True)
    price_at_purchase = Column(Float, nullable=False)  # Store the price at the time of purchase
    total_price = Column(Float, nullable=False, default=0)
    product = relationship('Product', uselist=False)
    product_variation = relationship('ProductVariation', uselist=False)

    def __repr__(self):
        return f"<OrderItem {self.product_id} - Quantity: {self.quantity}>"

# Shipping address model
class ShippingAddress(db.Model):
    __tablename__ = 'shipping_addresses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.uid'), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<ShippingAddress {self.address_line_1}, {self.city}>"

class Payment(db.Model):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.uid', name='fk_payment_user'), nullable=False)  # ForeignKey to Order model
    order_id = Column(Integer, ForeignKey('orders.id', name='fk_payment_order'), nullable=False)  # ForeignKey to Order model
    transaction_id = Column(String(100), unique=True, nullable=False)
    email = Column(String(120), nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_status = Column(String(20), default="Pending")  # Could be 'Pending', 'Paid', 'Failed', etc.
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))

    # Relationship with Order model
    order = db.relationship('Order', backref='payment', lazy=True)

    def __repr__(self):
        return f'<Payment {self.transaction_id}>'

# # Rating model for product reviews
# class Rating(db.Model):
#     id = Column(Integer, primary_key=True)
#     product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     rating = Column(Integer, nullable=False)  # Rating from 1-5
#     review = Column(Text, nullable=True)
#     created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))

#     def __repr__(self):
#         return f"<Rating {self.rating} for Product {self.product_id}>"


