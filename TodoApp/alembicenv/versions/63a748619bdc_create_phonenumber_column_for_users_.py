"""Create phonenumber column for users table

Revision ID: 63a748619bdc
Revises: 
Create Date: 2024-09-20 16:09:55.003389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63a748619bdc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number',sa.String(10),nullable=True))


def downgrade() -> None:
    op.drop_column('users','phone_number')
