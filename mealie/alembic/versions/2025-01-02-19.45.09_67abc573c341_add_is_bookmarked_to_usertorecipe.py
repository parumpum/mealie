"""add is_bookmarked to UserToRecipe

Revision ID: 67abc573c341
Revises: b1020f328e98
Create Date: 2025-01-02 19:45:09.045745

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "67abc573c341"
down_revision: str | None = "b1020f328e98"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("users_to_recipes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_bookmarked", sa.Boolean(), nullable=False))
        batch_op.create_index(batch_op.f("ix_users_to_recipes_is_bookmarked"), ["is_bookmarked"], unique=False)


def downgrade():
    with op.batch_alter_table("users_to_recipes", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_to_recipes_is_bookmarked"))
        batch_op.drop_column("is_bookmarked")
