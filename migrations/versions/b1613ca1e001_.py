"""empty message

Revision ID: b1613ca1e001
Revises: fd3edbd0263f
Create Date: 2023-05-21 16:33:48.104902

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b1613ca1e001'
down_revision = 'fd3edbd0263f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', postgresql.ARRAY(sa.String()), nullable=True))

    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', postgresql.ARRAY(sa.String()), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('genres')

    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('genres')

    # ### end Alembic commands ###
