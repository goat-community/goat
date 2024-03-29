"""added new field for outdated scenario feature

Revision ID: a052397bf699
Revises: f04bbdf8d861
Create Date: 2022-04-30 19:55:09.823166

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
import sqlmodel  



# revision identifiers, used by Alembic.
revision = 'a052397bf699'
down_revision = 'f04bbdf8d861'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('building_modified', sa.Column('outdated', sa.Boolean(), nullable=True), schema='customer')
    op.add_column('poi_modified', sa.Column('outdated', sa.Boolean(), nullable=True), schema='customer')
    op.add_column('way_modified', sa.Column('outdated', sa.Boolean(), nullable=True), schema='customer')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('way_modified', 'outdated', schema='customer')
    op.drop_column('poi_modified', 'outdated', schema='customer')
    op.drop_column('building_modified', 'outdated', schema='customer')
    # ### end Alembic commands ###
