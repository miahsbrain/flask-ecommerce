from project.models.products import Product, ProductVariation, ProductVariationImage, Cart, CartItem, Brand, Color, Highlight, Order, OrderItem, ShippingAddress, Payment
from run import main_app
from project.extensions.dependencies import db

with main_app.app_context():
    Product.query.delete()
    ProductVariation.query.delete()
    ProductVariationImage.query.delete()
    Cart.query.delete()
    CartItem.query.delete()
    Brand.query.delete()
    Color.query.delete()
    Highlight.query.delete()
    Order.query.delete()
    OrderItem.query.delete()
    ShippingAddress.query.delete()
    Payment.query.delete()
    db.session.commit()