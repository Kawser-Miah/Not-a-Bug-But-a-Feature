"""add step tracking to roadmap and tasks

Revision ID: 92bef48be32c
Revises: c82c0267485b
Create Date: 2025-09-24 14:20:39.974370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92bef48be32c'
down_revision: Union[str, Sequence[str], None] = 'c82c0267485b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema (no-op; included in initial migration)."""
    pass


def downgrade() -> None:
    """Downgrade schema (no-op)."""
    pass
