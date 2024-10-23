"""empty message

Revision ID: fbc539006daa
Revises: 38e0ad3f0b93
Create Date: 2024-10-23 21:08:36.964162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbc539006daa'
down_revision = '38e0ad3f0b93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_variations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('size_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_product_variations_sizes', 'sizes', ['size_id'], ['id'])
        batch_op.drop_column('_size')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_variations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_size', sa.VARCHAR(length=50), nullable=True))
        batch_op.drop_constraint('fk_product_variations_sizes', type_='foreignkey')
        batch_op.drop_column('size_id')

    # ### end Alembic commands ###
