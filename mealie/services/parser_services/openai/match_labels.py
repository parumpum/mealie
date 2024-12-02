import asyncio
import json
from collections.abc import Awaitable

from mealie.schema.openai.food_label import OpenAIFoodLabel, OpenAIFoodLabels
from mealie.schema.recipe.recipe_ingredient import ParsedIngredient
from mealie.services.openai import OpenAIDataInjection, OpenAIService

from .._base import IngredientLabel


class OpenAILabelMatcher(IngredientLabel):
    def _match_label(self, openai_ing: OpenAIFoodLabel) -> ParsedIngredient:
        return self.find_ingredient_label_match(openai_ing.food, openai_ing.label)

    def _get_prompt(self, service: OpenAIService) -> str:
        data_injections = [
            OpenAIDataInjection(
                description=(
                    "This is the JSON response schema. You must respond in valid JSON that follows this schema. "
                    "Your payload should be as compact as possible, eliminating unncessesary whitespace. Any fields "
                    "with default values which you do not populate should not be in the payload."
                ),
                value=OpenAIFoodLabels,
            ),
        ]

        if service.send_db_data and self.data_matcher.labels_by_alias:
            data_injections.extend(
                [
                    OpenAIDataInjection(
                        description=(
                            "Below is a list of labels found in the labels database. While parsing, you should "
                            "reference this list when determining which category the food fits in. You may "
                            "find a label in the input that does not have a good match. This should not prevent "
                            "you from placing that food into the Other category, however it may lower your confidence."
                        ),
                        value=list(set(self.data_matcher.labels_by_alias)),
                    ),
                ]
            )

        return service.get_prompt("ingredients.populate-food-labels", data_injections=data_injections)

    async def _match(self, ingredients: list[str]) -> OpenAIFoodLabels:
        service = OpenAIService()
        prompt = self._get_prompt(service)

        # chunk ingredients and send each chunk to its own worker. 20 ingredients per chunk
        ingredient_chunks = self._chunk_messages(ingredients, n=20)
        tasks: list[Awaitable[str | None]] = []
        for ingredient_chunk in ingredient_chunks:
            message = (
                "Below is the list of ingredients to categorize, each ingredient is enclosed in quotes:\n"
                + json.dumps(ingredient_chunk, separators=(",", ":"))
            )

            tasks.append(service.get_response(prompt, message, force_json_response=True))

        # re-combine chunks into one response
        try:
            responses_json = await asyncio.gather(*tasks)
        except Exception as e:
            raise Exception("Failed to call OpenAI services") from e

        try:
            responses = [
                OpenAIFoodLabels.parse_openai_response(response_json)
                for response_json in responses_json
                if responses_json
            ]
        except Exception as e:
            raise Exception("Failed to parse OpenAI response") from e

        if not responses:
            raise Exception("No response from OpenAI")

        labels = [label for response in responses for label in response.ingredientsLabeled]

        return OpenAIFoodLabels(ingredientsLabeled=labels)

    @staticmethod
    def _chunk_messages(messages: list[str], n=1) -> list[list[str]]:
        if n < 1:
            n = 1
        return [messages[i : i + n] for i in range(0, len(messages), n)]

    async def match(self, ingredients: list[str]) -> list[ParsedIngredient]:
        response = await self._match(ingredients)
        return [self._match_label(ing) for ing in response.ingredientsLabeled]
