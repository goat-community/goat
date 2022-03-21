"""removed deleted from scenario and edit type to building

Revision ID: 2ac47db804a1
Revises: ff7f51f0ca16
Create Date: 2022-03-19 10:33:35.847583

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
import sqlmodel  

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2ac47db804a1'
down_revision = 'ff7f51f0ca16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('building_modified', sa.Column('edit_type', sa.Text(), nullable=False), schema='customer')
    op.create_index(op.f('ix_customer_building_modified_edit_type'), 'building_modified', ['edit_type'], unique=False, schema='customer')
    op.drop_column('scenario', 'deleted_buildings', schema='customer')
    op.drop_column('scenario', 'deleted_pois', schema='customer')
    op.drop_column('scenario', 'deleted_ways', schema='customer')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scenario', sa.Column('deleted_ways', postgresql.ARRAY(sa.INTEGER()), server_default=sa.text("'{}'::integer[]"), autoincrement=False, nullable=True), schema='customer')
    op.add_column('scenario', sa.Column('deleted_pois', postgresql.ARRAY(sa.TEXT()), server_default=sa.text("'{}'::text[]"), autoincrement=False, nullable=True), schema='customer')
    op.add_column('scenario', sa.Column('deleted_buildings', postgresql.ARRAY(sa.INTEGER()), server_default=sa.text("'{}'::integer[]"), autoincrement=False, nullable=True), schema='customer')
    op.drop_index(op.f('ix_customer_building_modified_edit_type'), table_name='building_modified', schema='customer')
    op.drop_column('building_modified', 'edit_type', schema='customer')
    # ### end Alembic commands ###