"""add_region_to_wine_summaries

Revision ID: 84b652a43b3c
Revises: 16f720f64493
Create Date: 2025-05-23 20:17:59.779045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84b652a43b3c'
down_revision: Union[str, None] = '16f720f64493'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('wine_summaries', sa.Column('region', sa.String(length=255), nullable=False, server_default=sa.text("''")))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('wine_summaries', 'region')
