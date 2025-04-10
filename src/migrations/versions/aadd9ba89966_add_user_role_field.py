"""Add user role field

Revision ID: aadd9ba89966
Revises: a9bb57b46b15
Create Date: 2025-02-04 02:54:59.839225

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "aadd9ba89966"
down_revision: Union[str, None] = "a9bb57b46b15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = postgresql.ENUM("admin", "staff", "active", name="role")


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Create the new enum type
    role_enum.create(op.get_bind())

    # Add the new column to the user table
    op.add_column(
        "user", sa.Column("role", role_enum, nullable=True, server_default="active")
    )

    op.create_index(op.f("ix_user_role"), "user", ["role"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_role"), table_name="user")
    op.drop_column("user", "role")

    role_enum.drop(op.get_bind())
    # ### end Alembic commands ###
