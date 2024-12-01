"""add household auto food label

Revision ID: 109308909303
Revises: b1020f328e98
Create Date: 2024-12-01 14:53:48.822530

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "109308909303"
down_revision: str | None = "b1020f328e98"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("household_preferences", schema=None) as household_preferences:
        household_preferences.add_column(sa.Column("food_auto_label", sa.Boolean(), server_default="false"))


def downgrade():
    with op.batch_alter_table("household_preferences", schema=None) as household_preferences:
        household_preferences.drop_column(sa.Column("food_auto_label", sa.Boolean(), server_default="false"))
