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

    user_id = Column(Integer, ForeignKey('users.uid', name='fk_product_user'))
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
    stock = Column(Integer, nullable=False)  # Stock for this variation

    product_id = Column(Integer, ForeignKey('products.id', name='fk_product_variation_product'), nullable=False)

    # Relationship to ProductVariationImage
    images = relationship('ProductVariationImage', backref='variation', lazy=True)

    def __repr__(self):
        return f'<ProductVariation {self.color} {self.size}>'


class ProductVariationImage(db.Model):
    __tablename__ = 'product_variation_images'

    id = Column(Integer, primary_key=True)
    image_url = Column(String(255), nullable=False)  # URL or path to the image

    variation_id = Column(Integer, ForeignKey('product_variations.id', name='fk_product_variation_images_product_variation'), nullable=False)

    def __repr__(self):
        return f'<ProductVariationImage {self.image_url}>'


# Product model to store basic product information
# class Product(db.Model):
#     id = Column(Integer, primary_key=True)
#     name = Column(String(150), nullable=False)
#     description = Column(Text, nullable=False)
#     price = Column(Float, nullable=False)
#     stock = Column(Integer, default=0)
#     category = Column(String(50), nullable=False)
#     created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
#     updated_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

#     # One product can have multiple images
#     images = db.relationship('ProductImage', backref='product', lazy=True)
    
#     # One product can have multiple variations (e.g., colors, sizes)
#     variations = db.relationship('ProductVariation', backref='product', lazy=True)

#     def __repr__(self):
#         return f"<Product {self.name}>"

# # Model to store product images
# class ProductImage(db.Model):
#     id = Column(Integer, primary_key=True)
#     product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
#     image_url = Column(String(255), nullable=False)

#     def __repr__(self):
#         return f"<ProductImage {self.image_url}>"

# # Product variations such as color, size, etc.
# class ProductVariation(db.Model):
#     id = Column(Integer, primary_key=True)
#     product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
#     color = Column(String(50), nullable=True)
#     size = Column(String(50), nullable=True)
#     stock = Column(Integer, default=0)  # Stock per variation
#     price = Column(Float, nullable=True)  # Different prices per variation

#     def __repr__(self):
#         return f"<ProductVariation {self.color} - {self.size}>"

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

# # Shopping Cart model to store user's cart items before checkout
# class CartItem(db.Model):
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
#     quantity = Column(Integer, default=1)
#     variation_id = Column(Integer, ForeignKey('product_variation.id'), nullable=True)  # Store selected variation

#     def __repr__(self):
#         return f"<CartItem {self.product_id} - Quantity: {self.quantity}>"

# # Order model to store information about the order
# class Order(db.Model):
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     total_price = Column(Float, nullable=False)
#     status = Column(String(50), default="Pending")  # Pending, Shipped, Delivered
#     created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
#     updated_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

#     # One order can have multiple items
#     order_items = relationship('OrderItem', backref='order', lazy=True)

#     # Shipping address for the order
#     shipping_address_id = Column(Integer, ForeignKey('shipping_address.id'), nullable=False)

#     def __repr__(self):
#         return f"<Order {self.id} - Status: {self.status}>"

# # Items within an order
# class OrderItem(db.Model):
#     id = Column(Integer, primary_key=True)
#     order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
#     product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
#     quantity = Column(Integer, nullable=False)
#     variation_id = Column(Integer, ForeignKey('product_variation.id'), nullable=True)
#     price_at_purchase = Column(Float, nullable=False)  # Store the price at the time of purchase

#     def __repr__(self):
#         return f"<OrderItem {self.product_id} - Quantity: {self.quantity}>"

# # Shipping address model
# class ShippingAddress(db.Model):
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     address_line_1 = Column(String(255), nullable=False)
#     address_line_2 = Column(String(255), nullable=True)
#     city = Column(String(100), nullable=False)
#     state = Column(String(100), nullable=False)
#     zip_code = Column(String(20), nullable=False)
#     country = Column(String(100), nullable=False)

#     def __repr__(self):
#         return f"<ShippingAddress {self.address_line_1}, {self.city}>"
