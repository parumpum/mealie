import asyncio
import json
from collections.abc import Awaitable

from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.schema.openai.food_label import OpenAIFoodLabel, OpenAIFoodLabels
from mealie.schema.openai.recipe_ingredient import OpenAIIngredient, OpenAIIngredients
from mealie.schema.openai.recipe_nutrition import OpenAINutrition
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientConfidence,
    ParsedIngredient,
    RecipeIngredient,
)
from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.services.openai import OpenAIDataInjection, OpenAIService

from .._base import ABCIngredientParser, IngredientLabel


class OpenAINutritionParser:
    def __init__(self, group_id: UUID4, session: Session) -> None:
        self.group_id = group_id
        self.session = session

    def _get_prompt(self, service: OpenAIService) -> str:
        data_injections = [
            OpenAIDataInjection(
                description=(
                    "This is the JSON response schema. You must respond in valid JSON that follows this schema. "
                    "Your payload should be as compact as possible, eliminating unncessesary whitespace. Any fields "
                    "with default values which you do not populate should not be in the payload."
                ),
                value=OpenAINutrition,
            ),
        ]

        return service.get_prompt("recipes.fetch-recipe-nutrition", data_injections=data_injections)

    async def fetch(self, ingredients: str) -> Nutrition:
        service = OpenAIService()
        prompt = self._get_prompt(service)

        tasks: list[Awaitable[str | None]] = []

        message = json.dumps(ingredients, separators=(",", ":"))

        tasks.append(service.get_response(prompt, message, force_json_response=True))

        # re-combine chunks into one response
        try:
            responses_json = await asyncio.gather(*tasks)
        except Exception as e:
            raise Exception("Failed to call OpenAI services") from e

        try:
            responses = [
                OpenAINutrition.parse_openai_response(response_json)
                for response_json in responses_json
                if responses_json
            ]
        except Exception as e:
            raise Exception("Failed to parse OpenAI response") from e

        if not responses:
            raise Exception("No response from OpenAI")

        if responses and responses[0].nutrition:
            nutritional_info = responses[0].nutrition
        else:
            nutritional_info = Nutrition()

        return nutritional_info

    @staticmethod
    def _chunk_messages(messages: list[str], n=1) -> list[list[str]]:
        if n < 1:
            n = 1
        return [messages[i : i + n] for i in range(0, len(messages), n)]


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

    #     {
    #   "ingredientsLabeled": [
    #     {
    #       "input": "vanilla",
    #       "food": "vanilla",
    #       "label": "Spices",
    #       "confidence": 100
    #     },
    #     {
    #       "input": "vegetables",
    #       "food": "vegetables",
    #       "label": "Vegetables",
    #       "confidence": 100
    #     }
    #   ]
    # }

    @staticmethod
    def _chunk_messages(messages: list[str], n=1) -> list[list[str]]:
        if n < 1:
            n = 1
        return [messages[i : i + n] for i in range(0, len(messages), n)]

    async def match(self, ingredients: list[str]) -> list[ParsedIngredient]:
        response = await self._match(ingredients)
        return [self._match_label(ing) for ing in response.ingredientsLabeled]


class OpenAIParser(ABCIngredientParser):
    def _convert_ingredient(self, openai_ing: OpenAIIngredient) -> ParsedIngredient:
        ingredient = RecipeIngredient(
            original_text=openai_ing.input,
            quantity=openai_ing.quantity,
            unit=CreateIngredientUnit(name=openai_ing.unit) if openai_ing.unit else None,
            food=CreateIngredientFood(name=openai_ing.food) if openai_ing.food else None,
            note=openai_ing.note,
        )

        parsed_ingredient = ParsedIngredient(
            input=openai_ing.input,
            confidence=IngredientConfidence(average=openai_ing.confidence),
            ingredient=ingredient,
        )

        return self.find_ingredient_match(parsed_ingredient)

    def _get_prompt(self, service: OpenAIService) -> str:
        data_injections = [
            OpenAIDataInjection(
                description=(
                    "This is the JSON response schema. You must respond in valid JSON that follows this schema. "
                    "Your payload should be as compact as possible, eliminating unncessesary whitespace. Any fields "
                    "with default values which you do not populate should not be in the payload."
                ),
                value=OpenAIIngredients,
            ),
        ]

        if service.send_db_data and self.data_matcher.units_by_alias:
            data_injections.extend(
                [
                    OpenAIDataInjection(
                        description=(
                            "Below is a list of units found in the units database. While parsing, you should "
                            "reference this list when determining which part of the input is the unit. You may "
                            "find a unit in the input that does not exist in this list. This should not prevent "
                            "you from parsing that text as a unit, however it may lower your confidence level."
                        ),
                        value=list(set(self.data_matcher.units_by_alias)),
                    ),
                ]
            )

        return service.get_prompt("recipes.parse-recipe-ingredients", data_injections=data_injections)

    @staticmethod
    def _chunk_messages(messages: list[str], n=1) -> list[list[str]]:
        if n < 1:
            n = 1
        return [messages[i : i + n] for i in range(0, len(messages), n)]

    async def _parse(self, ingredients: list[str]) -> OpenAIIngredients:
        service = OpenAIService()
        prompt = self._get_prompt(service)

        # chunk ingredients and send each chunk to its own worker
        ingredient_chunks = self._chunk_messages(ingredients, n=service.workers)
        tasks: list[Awaitable[str | None]] = []
        for ingredient_chunk in ingredient_chunks:
            message = json.dumps(ingredient_chunk, separators=(",", ":"))
            tasks.append(service.get_response(prompt, message, force_json_response=True))

        # re-combine chunks into one response
        try:
            responses_json = await asyncio.gather(*tasks)
        except Exception as e:
            raise Exception("Failed to call OpenAI services") from e

        try:
            responses = [
                OpenAIIngredients.parse_openai_response(response_json)
                for response_json in responses_json
                if responses_json
            ]
        except Exception as e:
            raise Exception("Failed to parse OpenAI response") from e

        if not responses:
            raise Exception("No response from OpenAI")

        return OpenAIIngredients(
            ingredients=[ingredient for response in responses for ingredient in response.ingredients]
        )

    async def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        items = await self.parse([ingredient_string])
        return items[0]

    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        response = await self._parse(ingredients)
        return [self._convert_ingredient(ing) for ing in response.ingredients]
