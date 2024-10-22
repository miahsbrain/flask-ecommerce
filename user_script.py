# populate_sku.py
# from project.extensions.dependencies import db
# from project.models.users import User
# from run import main_app

# with main_app.app_context():
#     # Fetch all products
#     users = User.query.all()

#     # Assign unique values to the 'sku' field for each product
#     for i, user in enumerate(users):
#         if not user.phone:  # If the SKU is missing
#             user.phone = f"{5555555555+1}"  # Assign a unique SKU
#         else:
#             # Optionally check for duplicates and handle them
#             pass

#     db.session.commit()  # Save changes to the database

from uuid import uuid1
print(uuid1().int)