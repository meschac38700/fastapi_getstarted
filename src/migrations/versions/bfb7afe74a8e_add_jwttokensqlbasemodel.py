"""Add JWTTokenSQLBaseModel

Revision ID: bfb7afe74a8e
Revises: d5afe7853949
Create Date: 2025-01-29 07:49:47.188637

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bfb7afe74a8e"
down_revision: Union[str, None] = "d5afe7853949"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "jwttoken",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("jwttoken", "created_at")
    # ### end Alembic commands ###
