from project.models.base import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Float, DateTime
from datetime import datetime, timezone
from project.extensions.dependencies import db
from sqlalchemy.orm import relationship

class Product(BaseModel):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)  # Base price, can be overridden by variation
    stock = Column(Integer, nullable=False, default=1)  # General stock, variations override if needed

    user_id = Column(Integer, ForeignKey('users.uid', name='fk_products_user'))
    # Relationship to ProductVariation
    variations = relationship('ProductVariation', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductVariation(BaseModel):
    __tablename__ = 'product_variations'

    id = Column(Integer, primary_key=True)
    color = Column(String(50), nullable=False)  # Color variation
    size = Column(String(50), nullable=True)  # Size variation, optional
    price = Column(Float, nullable=False)  # Price specific to this variation
    stock = Column(Integer, nullable=False, default=1)  # Stock for this variation

    product_id = Column(Integer, ForeignKey('products.id', name='fk_product_variations_product'), nullable=False)

    # Relationship to ProductVariationImage
    images = relationship('ProductVariationImage', backref='variation', lazy=True)

    def __repr__(self):
        return f'<ProductVariation {self.color} {self.size}>'


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
    status = Column(String(50), default="Pending")  # Pending, Confirmed, Shipped, Delivered

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


