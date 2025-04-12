"""added column

Revision ID: 09559ba0259d
Revises: 61f6a837b7b3
Create Date: 2025-04-11 21:01:44.855275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09559ba0259d'
down_revision: Union[str, None] = '61f6a837b7b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('time_summary', sa.Column('day_start_time', sa.DateTime(), nullable=True))
    op.add_column('time_summary', sa.Column('day_end_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('time_summary', 'day_end_time')
    op.drop_column('time_summary', 'day_start_time')
    # ### end Alembic commands ###
