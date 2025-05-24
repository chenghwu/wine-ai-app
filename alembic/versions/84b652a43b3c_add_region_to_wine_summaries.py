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
    # Step 1: Add the region column as nullable initially
    op.add_column('wine_summaries', sa.Column('region', sa.String(length=255), nullable=True))

    # Step 2: Backfill existing rows
    wine_summaries_table = sa.sql.table('wine_summaries', sa.sql.column('region', sa.String))
    op.execute(wine_summaries_table.update().where(wine_summaries_table.c.region.is_(None)).values(region=''))

    # Step 3: Alter the column to be non-nullable and set server default
    op.alter_column('wine_summaries', 'region', existing_type=sa.String(length=255), nullable=False, server_default=sa.text("''"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('wine_summaries', 'region')