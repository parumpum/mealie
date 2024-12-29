from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel


class RecipeAssociationCreate(MealieModel):
    recipe_id: UUID4
    associated_recipe_id: UUID4
    quantity: float
    file_name: str | None = None
    model_config = ConfigDict(from_attributes=True)
