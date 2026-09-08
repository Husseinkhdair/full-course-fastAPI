"""create posts table

Revision ID: b1e2c3d4e5f6
Revises: aea8918985e1
Create Date: 2026-09-08 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1e2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'aea8918985e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'Posts',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.String(length=255), nullable=False),
        sa.Column('author_role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.String(length=100), nullable=False),
        sa.Column('updated_at', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('Posts')
