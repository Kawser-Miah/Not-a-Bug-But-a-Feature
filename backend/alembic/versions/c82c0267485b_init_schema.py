"""init schema

Revision ID: c82c0267485b
Revises: 
Create Date: 2025-09-24 11:34:44.654115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c82c0267485b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('uuid', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('time_duration', sa.Integer(), nullable=False),
        sa.Column('interests', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # roadmaps (with current_step)
    op.create_table(
        'roadmaps',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
    )

    # tasks (with step_num and sources)
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('roadmap_id', sa.Integer(), sa.ForeignKey('roadmaps.id'), nullable=False),
        sa.Column('step_num', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('assigned_time', sa.DateTime(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
    )

    # task_failures
    op.create_table(
        'task_failures',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=False),
        sa.Column('failure_date', sa.DateTime(), nullable=True),
        sa.Column('tasks_completed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tasks_count', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('task_failures')
    op.drop_table('tasks')
    op.drop_table('roadmaps')
    op.drop_table('users')
