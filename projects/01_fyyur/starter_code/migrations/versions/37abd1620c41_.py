"""empty message

Revision ID: 37abd1620c41
Revises: 96e5ecf39bc9
Create Date: 2020-10-29 09:00:59.894797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37abd1620c41'
down_revision = '96e5ecf39bc9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    op.alter_column('venues', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venues', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.alter_column('artists', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    # ### end Alembic commands ###
