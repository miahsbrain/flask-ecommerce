"""empty message

Revision ID: 314cb97fce52
Revises: ca6d890a9c0a
Create Date: 2024-10-23 20:40:44.581095

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '314cb97fce52'
down_revision = 'ca6d890a9c0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.alter_column('highlight',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=150),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('highlights', schema=None) as batch_op:
        batch_op.alter_column('highlight',
               existing_type=sa.String(length=150),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)

    # ### end Alembic commands ###
