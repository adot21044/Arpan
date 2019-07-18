"""empty message

Revision ID: 2e853079129f
Revises: d638564c7da3
Create Date: 2019-06-16 13:46:08.285295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e853079129f'
down_revision = 'd638564c7da3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.drop_column('users', 'password')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###