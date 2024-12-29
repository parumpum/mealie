from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, UniqueConstraint, orm
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .recipe import RecipeModel


class RecipeAssociationsModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_associations"
    # __table_args__ = (UniqueConstraint("name", "group_id", name="multi_purpose_labels_name_group_id_key"),)
    __table_args__ = (UniqueConstraint("recipe_id", "associated_recipe_id", name="uq_recipe_associated_recipe"),)

    recipe_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("recipes.id"), nullable=False)
    associated_recipe_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("recipes.id"), nullable=False)

    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    recipe: Mapped[RecipeModel] = orm.relationship(
        "RecipeModel", foreign_keys=[recipe_id], back_populates="associations"
    )
    associated_recipe: Mapped[RecipeModel] = orm.relationship("RecipeModel", foreign_keys=[associated_recipe_id])

    @auto_init()
    def __init__(self, **_) -> None:
        pass
