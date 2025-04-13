"""change column name

Revision ID: 61f6a837b7b3
Revises: 529016b4d688
Create Date: 2025-04-11 20:06:57.720808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61f6a837b7b3'
down_revision: Union[str, None] = '529016b4d688'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('time_summary', sa.Column('overtime_seconds', sa.Integer(), nullable=True))
    op.add_column('time_summary', sa.Column('actual_seconds', sa.Integer(), nullable=True))
    op.add_column('time_summary', sa.Column('min_seconds', sa.Integer(), nullable=True))
    op.drop_column('time_summary', 'actual_hours')
    op.drop_column('time_summary', 'min_hours')
    op.drop_column('time_summary', 'overtime_hours')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('time_summary', sa.Column('overtime_hours', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('time_summary', sa.Column('min_hours', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('time_summary', sa.Column('actual_hours', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('time_summary', 'min_seconds')
    op.drop_column('time_summary', 'actual_seconds')
    op.drop_column('time_summary', 'overtime_seconds')
    # ### end Alembic commands ###
