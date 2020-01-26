"""empty message

Revision ID: 460b0528c202
Revises: 108c4cf52be6
Create Date: 2020-01-20 02:47:19.789296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '460b0528c202'
down_revision = '108c4cf52be6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('quarterly_request_user_id_fkey', 'quarterly_request', type_='foreignkey')
    op.create_foreign_key(None, 'quarterly_request', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'quarterly_request', type_='foreignkey')
    op.create_foreign_key('quarterly_request_user_id_fkey', 'quarterly_request', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###
