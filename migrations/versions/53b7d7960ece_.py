"""empty message

Revision ID: 53b7d7960ece
Revises: b1613ca1e001
Create Date: 2023-05-21 16:58:04.243009

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '53b7d7960ece'
down_revision = 'b1613ca1e001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.alter_column('genres',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=False)

    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('artist_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'Artist', ['artist_id'], ['id'])

    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.alter_column('genres',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.alter_column('genres',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=True)

    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('artist_id')

    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.alter_column('genres',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=True)

    # ### end Alembic commands ###
