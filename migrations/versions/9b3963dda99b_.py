"""empty message

Revision ID: 9b3963dda99b
Revises: 2d535021ae83
Create Date: 2024-10-19 16:09:07.614025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b3963dda99b'
down_revision = '2d535021ae83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cart_id', sa.Integer(), nullable=False))
        batch_op.drop_constraint('fk_cart_items_user', type_='foreignkey')
        batch_op.create_foreign_key('fk_cart_items_cart', 'carts', ['cart_id'], ['id'])
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), nullable=False))
        batch_op.drop_constraint('fk_cart_items_cart', type_='foreignkey')
        batch_op.create_foreign_key('fk_cart_items_user', 'users', ['user_id'], ['uid'])
        batch_op.drop_column('cart_id')

    # ### end Alembic commands ###
