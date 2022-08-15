"""empty message

Revision ID: 93a4df3f3b10
Revises: 7e07e654204b, 786395e0b1f4
Create Date: 2022-08-11 11:40:32.843034

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
import sqlmodel  



# revision identifiers, used by Alembic.
revision = '93a4df3f3b10'
down_revision = ('7e07e654204b', '786395e0b1f4')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
