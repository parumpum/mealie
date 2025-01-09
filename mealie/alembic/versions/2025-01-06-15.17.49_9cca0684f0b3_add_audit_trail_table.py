"""add audit_trail table

Revision ID: 9cca0684f0b3
Revises: b1020f328e98
Create Date: 2025-01-06 15:17:49.608596

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types
from mealie.db.models._model_utils import datetime

# revision identifiers, used by Alembic.
revision = "9cca0684f0b3"
down_revision: str | None = "b1020f328e98"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def get_db_type():
    return op.get_context().dialect.name


def upgrade():
    # Create RecipeHistory table
    op.create_table(
        "recipe_history",
        sa.Column("id", mealie.db.migration_types.GUID(), primary_key=True, autoincrement=True),
        sa.Column(
            "recipe_id",
            mealie.db.migration_types.GUID(),
            sa.ForeignKey("recipe.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", mealie.db.migration_types.GUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "parent_revision_id",
            mealie.db.migration_types.GUID(),
            sa.ForeignKey("recipe_history.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("revision_timestamp", sa.DateTime, server_default=datetime.get_utc_now(), nullable=False),
        # Store serialized recipe data (e.g., JSON)
        sa.Column("old_data", sa.Text, nullable=False),
        # Store serialized recipe data (e.g., JSON)')
        sa.Column("new_data", sa.Text, nullable=False),
    )
    op.create_index(op.f("ix_recipe_history_user_id"), "recipe_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_recipe_history_recipe_id"), "recipe_history", ["recipe_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_recipe_history_user_id"), table_name="recipe_history")
    op.drop_index(op.f("ix_recipe_history_recipe_id"), table_name="recipe_history")
    op.drop_table("recipe_history")
