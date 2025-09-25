"""remove_uuid_and_username_from_users

Revision ID: 7b5238fcf721
Revises: 92bef48be32c
Create Date: 2025-09-24 17:40:38.417351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b5238fcf721'
down_revision: Union[str, Sequence[str], None] = '92bef48be32c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove uuid and username columns from users table."""
    # Drop indices first to avoid constraint violations
    try:
        op.drop_index('ix_users_uuid', table_name='users')
    except:
        pass  # Index might not exist or already dropped
    
    try:
        op.drop_index('ix_users_username', table_name='users') 
    except:
        pass  # Index might not exist or already dropped
    
    # Remove uuid column
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('uuid')
        batch_op.drop_column('username')


def downgrade() -> None:
    """Add back uuid and username columns to users table."""
    # Add back uuid and username columns
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.String(), nullable=False, unique=True))
        batch_op.add_column(sa.Column('username', sa.String(), nullable=False, unique=True))
    
    # Recreate indices
    op.create_index('ix_users_uuid', 'users', ['uuid'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
