"""empty message

Revision ID: fd3edbd0263f
Revises: b7a324e709d3
Create Date: 2023-05-21 16:33:00.922567

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fd3edbd0263f'
down_revision = 'b7a324e709d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('genres')

    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('genres')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=False))

    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
