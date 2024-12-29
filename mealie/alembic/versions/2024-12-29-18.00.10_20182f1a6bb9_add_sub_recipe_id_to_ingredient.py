"""add sub_recipe_id to ingredient

Revision ID: 20182f1a6bb9
Revises: b1020f328e98
Create Date: 2024-12-29 18:00:10.698690

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "20182f1a6bb9"
down_revision: str | None = "b1020f328e98"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("recipes_ingredients", schema=None) as batch_op:
        # sub_recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
        # sub_recipe: Mapped["RecipeModel"] = relationship("RecipeModel", foreign_keys=[sub_recipe_id])
        batch_op.add_column(sa.Column("sub_recipe_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_foreign_key(
            "fk_sub_recipe_id",
            "recipes",
            ["sub_recipe_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("recipes_ingredients", schema=None) as batch_op:
        batch_op.drop_column("sub_recipe_id")
