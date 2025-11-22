import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

export type MealsByDate = {
  date: Date;
  meals: ReadPlanEntry[];
};

export type MealPlanViewMode = "daily" | "weekly";

export interface MealPlanSettings {
  viewMode: MealPlanViewMode;
  weekStartDay: number; // 0=Monday, 6=Sunday
};

export type WeeklyMealPlan = {
  weekStart: Date;
  weekEnd: Date;
  days: MealsByDate[];
  allMeals: ReadPlanEntry[]; // Flat list of all meals in the week
};
