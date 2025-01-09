from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID

from .._model_utils.auto_init import auto_init

if TYPE_CHECKING:
    from . import RecipeModel


class RecipeHistoryModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_history"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"))
    parent_revision_id = Column(Integer, ForeignKey("recipe_revisions.id"), nullable=True)
    revision_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Store recipe data as JSON or a reference to a file
    old_data = Column(Text, nullable=False)
    new_data = Column(Text, nullable=False)
    recipe: Mapped["RecipeModel"] = relationship("RecipeModel", back_populates="revisions")

    parent_revision = relationship("RecipeHistory", remote_side=[id], backref="child_revisions")

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise AttributeError(
                f"Cannot modify attribute '{
                                 key}' of immutable instance"
            )
        super().__setattr__(key, value)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
