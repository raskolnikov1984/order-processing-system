"""seed inventory data

Revision ID: 86ab89d0424d
Revises: 30600bbdf8d5
Create Date: 2025-12-17 17:25:00.912155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86ab89d0424d'
down_revision: Union[str, Sequence[str], None] = '30600bbdf8d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    inventory_table = sa.table(
        'inventory',
        sa.column('product_id', sa.String),
        sa.column('forecast_quantity', sa.Float)
    )

    op.bulk_insert(
        inventory_table,
        [
            {'product_id': 'prod-1', 'forecast_quantity': 150.0},
            {'product_id': 'prod-2', 'forecast_quantity': 200.0},
            {'product_id': 'prod-3', 'forecast_quantity': 75.5},
            {'product_id': 'prod-4', 'forecast_quantity': 300.0},
        ]
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
            "DELETE FROM inventory WHERE product_id IN ('prod-1', 'prod-2', 'prod-3', 'prod-4')"
            )
