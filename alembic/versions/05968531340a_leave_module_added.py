"""leave module added

Revision ID: 05968531340a
Revises: 09559ba0259d
Create Date: 2025-04-15 14:15:01.498112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05968531340a'
down_revision: Union[str, None] = '09559ba0259d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leave_type',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('carry_forward', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('leave_balance',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('leave_type', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('quarter', sa.Integer(), nullable=False),
    sa.Column('leave_available', sa.Integer(), nullable=False),
    sa.Column('leave_taken', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['leave_type'], ['leave_type.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'leave_type', 'year', 'quarter', name='uq_leave_balance_period')
    )
    op.create_table('leave_requests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('leave_type', sa.UUID(), nullable=False),
    sa.Column('application_date', sa.DateTime(), nullable=False),
    sa.Column('leave_from', sa.DateTime(), nullable=False),
    sa.Column('leave_to', sa.DateTime(), nullable=False),
    sa.Column('leave_reason', sa.String(length=255), nullable=False),
    sa.Column('leave_status', sa.String(length=40), nullable=False),
    sa.Column('approved_date', sa.DateTime(), nullable=True),
    sa.Column('approver_comments', sa.String(length=40), nullable=True),
    sa.Column('approver_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['leave_type'], ['leave_type.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('leave_requests')
    op.drop_table('leave_balance')
    op.drop_table('leave_type')
    # ### end Alembic commands ###
