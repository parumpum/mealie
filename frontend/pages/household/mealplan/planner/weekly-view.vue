<template>
  <v-container class="mx-0 my-3 pa">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-btn icon @click="previousWeek">
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
        <v-spacer />
        <span>
          {{ formatWeekRange(currentWeekStart) }}
        </span>
        <v-spacer />
        <v-btn icon @click="nextWeek">
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Meal Pool Section -->
        <v-card class="mb-4 pa-4 border-left-primary">
          <v-card-title class="text-h6">
            {{ $t("meal-plan.meal-pool") }}
          </v-card-title>
          <v-card-text>
            <!-- <VueDraggable
              v-model="weeklyMeals"
              group="meals"
              class="d-flex flex-wrap gap-2"
            > -->
            <VueDraggable
              v-model="weeklyMeals"
              tag="div"
              handle=".handle"
              :delay="250"
              :delay-on-touch-only="true"
              group="meals"
              style="min-height: 150px"
            >
              <RecipeCardMobile
                v-for="meal in weeklyMeals"
                :key="meal.id"
                :recipe-id="meal.recipe ? meal.recipe.id! : ''"
                class="mb-2"
                :rating="meal.recipe ? meal.recipe.rating! : 0"
                :slug="meal.recipe ? meal.recipe.slug! : meal.title!"
                :description="meal.recipe ? meal.recipe.description! : meal.text!"
                :name="meal.recipe ? meal.recipe.name! : meal.title!"
                :tags="meal.recipe ? meal.recipe.tags! : []"
              />
            </VueDraggable>
          </v-card-text>
        </v-card>

      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import { startOfWeek, endOfWeek, addWeeks, eachDayOfInterval, format, isSameDay, parseISO } from "date-fns";
import type { MealsByDate, WeeklyMealPlan } from "./types";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";

interface Props {
  mealplans: MealsByDate[];
}

const props = defineProps<Props>();

const currentWeekStart = ref(startOfWeek(new Date(), { weekStartsOn: 1 })); // Monday
const showDayBreakdown = ref(false);

const weeklyPlan = computed<WeeklyMealPlan>(() => {
  const start = currentWeekStart.value;
  const end = endOfWeek(start, { weekStartsOn: 1 });
  const days = eachDayOfInterval({ start, end });

  const daysMapped = days.map((date) => {
    const mealsForDay = props.mealplans
      .filter((mealsByDate) => {
        const mealDate = typeof mealsByDate.date === "string" ? parseISO(mealsByDate.date) : new Date(mealsByDate.date);
        return isSameDay(mealDate, date);
      })
      .flatMap(mealsByDate => mealsByDate.meals);

    return {
      date,
      meals: mealsForDay,
    };
  });

  // Collect all meals into a single array
  const allMeals: ReadPlanEntry[] = [];
  props.mealplans.forEach((day) => {
    day.meals.forEach((meal) => {
      allMeals.push(meal);
    });
  });

  return {
    weekStart: start,
    weekEnd: end,
    days: daysMapped,
    allMeals,
  };
});

const weeklyMeals = computed({
  get: () => {
    const meals = weeklyPlan.value.allMeals;
    return meals;
  },
  set: (newMeals) => {
    // Handle reordering - emit event to parent
    emit("update:mealplans", newMeals);
  },
});

const emit = defineEmits<{
  (e: "update:mealplans", meals: ReadPlanEntry[]): void;
}>();

function previousWeek() {
  currentWeekStart.value = addWeeks(currentWeekStart.value, -1);
}

function nextWeek() {
  currentWeekStart.value = addWeeks(currentWeekStart.value, 1);
}

function formatWeekRange(start: Date) {
  const end = endOfWeek(start, { weekStartsOn: 1 });
  return `${format(start, "MMM d")} - ${format(end, "MMM d, yyyy")}`;
}

function formatDay(date: Date) {
  return format(date, "EEE, MMM d");
}
</script>

<style scoped>
.meal-card {
  width: 200px;
}

.day-meals {
  min-height: 100px;
}

.gap-2 {
  gap: 0.5rem;
}
</style>
