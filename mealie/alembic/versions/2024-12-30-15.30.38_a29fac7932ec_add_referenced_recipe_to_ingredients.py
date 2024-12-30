"""add referenced_recipe to ingredients

Revision ID: a29fac7932ec
Revises: b1020f328e98
Create Date: 2024-12-30 15:30:38.044709

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "a29fac7932ec"
down_revision: str | None = "b1020f328e98"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("recipes_ingredients", schema=None) as batch_op:
        batch_op.add_column(sa.Column("referenced_recipe_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_recipes_ingredients_referenced_recipe_id"), ["referenced_recipe_id"], unique=False
        )


def downgrade():
    with op.batch_alter_table("recipes_ingredients", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_recipes_ingredients_referenced_recipe_id"))
        batch_op.drop_column("referenced_recipe_id")
