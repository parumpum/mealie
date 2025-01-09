from pydantic import UUID4

from mealie.schema.recipe.recipe import Recipe
from mealie.services._base_service import BaseService


class RecipeHistoryService(BaseService):
    def __init__(self, recipe_id: UUID4) -> None:
        """
        RecipeHistoryService is a service that consolidates the reading/writing actions related
        to recipe history.
        """
        super().__init__()

        self.recipe_id = recipe_id

    def update_history(self, recipeId: UUID4, changes: dict) -> None:
        recipe = Recipe.get(recipeId)
        history = recipe.history
        history.append(changes)
        recipe.history = history
        recipe.save()

    # def get_history(self) -> list[Path]:
    #     return [x for x in self.dir_history.iterdir() if x.is_file()]

    # def write_history(self, data: dict) -> Path:
    #     history_file = self.dir_history.joinpath(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json")

    #     with open(history_file, "w") as f:
    #         json.dump(data, f, indent=4)

    #     return history_file

    # def delete_history(self, history_file: Path) -> None:
    #     history_file.unlink()
