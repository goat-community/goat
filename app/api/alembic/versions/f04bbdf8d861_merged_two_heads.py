"""merged two heads

Revision ID: f04bbdf8d861
Revises: 77ace648b3c7, 99c36dc4c2ff
Create Date: 2022-04-30 19:54:09.265556

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
import sqlmodel  



# revision identifiers, used by Alembic.
revision = 'f04bbdf8d861'
down_revision = ('77ace648b3c7', '99c36dc4c2ff')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
