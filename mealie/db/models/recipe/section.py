import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID
from mealie.db.models.recipe.ingredient import RecipeIngredientModel

from .._model_base import BaseMixins, SqlAlchemyBase


class RecipeIngredientSectionModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_ingredient_section"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    position: Mapped[int | None] = mapped_column(sa.Integer, index=True)

    recipe_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True, nullable=False)
    recipe_ingredient: Mapped[list["RecipeIngredientModel"]] = orm.relationship(
        "RecipeIngredientModel",
        cascade="all, delete-orphan",
        order_by="RecipeIngredientModel.position",
        collection_class=ordering_list("position"),
        foreign_keys="RecipeIngredientModel.section_id",
    )

    @auto_init()
    def __init__(self, **kwargs):
        pass


# Allow nested sections in future
# parent_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipe_ingredient_sections.id"), index=True)
# subsections: Mapped[list["RecipeIngredientSectionModel"]] = orm.relationship(
#     "RecipeIngredientSectionModel",
#     cascade="all, delete-orphan",
#     backref=orm.backref("parent", remote_side=[id]),
#     collection_class=ordering_list("position"),
#     foreign_keys="RecipeIngredientSectionModel.parent_id",
# )
