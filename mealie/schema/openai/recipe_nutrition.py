from textwrap import dedent

from pydantic import Field

from mealie.schema.recipe.recipe_nutrition import Nutrition

from ._base import OpenAIBase


class OpenAINutrition(OpenAIBase):
    input: str = Field(
        ...,
        description=dedent(
            """
            The input is simply the recipe string you are processing as-is. It is forbidden to
            modify this at all, you must provide the input exactly as you received it.
            """
        ),
    )
    confidence: float | None = Field(
        None,
        description=dedent(
            """
            This value is a float between 0 - 100, where 100 is full confidence that the result is correct,
            and 0 is no confidence that the result is correct. If you're unable to parse anything,
            and you put the entire string in the notes, you should return 0 confidence. If you can easily
            parse the string into each component, then you should return a confidence of 100. If you have to
            guess which part is the unit and which part is the food, your confidence should be lower, such as 60.
            Even if there is no unit or note, if you're able to determine the food, you may use a higher confidence.
            If the entire ingredient consists of only a food, you can use a confidence of 100.
            """
        ),
    )

    nutrition: Nutrition | None = Field(
        0,
        description=dedent(
            """
            A dictionary of the nutritional information for the recipe. The dictionary should contain the following:
            Calories, Carbohydrates, Cholesterol, Fat, Fiber, Protein, Saturated fat, Sodium, Sugar, trans-fat,
            and unsaturated fat.
            """
        ),
    )
