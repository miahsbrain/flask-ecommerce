from project.models.products import Product, ProductVariation, ProductVariationImage
from run import main_app
from project.extensions.dependencies import db

with main_app.app_context():
    # Create a new product
    new_product = Product(
        name="Stylish T-Shirt",
        description="A cool, stylish t-shirt available in multiple colors and sizes.",
        price=19.99,
        stock=100
    )
    db.session.add(new_product)
    db.session.commit()

    # Add variations for the product
    variation1 = ProductVariation(
        color="Red",
        size="M",
        price=19.99,
        stock=50,
        product_id=new_product.id
    )
    db.session.add(variation1)

    variation2 = ProductVariation(
        color="Blue",
        size="L",
        price=21.99,  # This variation has a different price
        stock=30,
        product_id=new_product.id
    )
    db.session.add(variation2)
    db.session.commit()

    # Add images for each variation
    image1 = ProductVariationImage(
        image_url="/app/img/shop/ladies-1.jpg",
        variation_id=variation1.id
    )
    db.session.add(image1)

    image2 = ProductVariationImage(
        image_url="/app/img/shop/ladies-2.jpg",
        variation_id=variation2.id
    )
    db.session.add(image2)

    db.session.commit()
