import { Ref } from "vue";
import { useData, useStore } from "../partials/use-store-factory";
import { ref } from "#imports";
import { IngredientUnit } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";

const store: Ref<IngredientUnit[]> = ref([]);
const loading = ref(false);

export const useUnitData = function () {
  return useData<IngredientUnit>({
    id: "",
    name: "",
    fraction: true,
    abbreviation: "",
    description: "",
  });
}

export const useUnitStore = function () {
  const api = useUserApi();
  return useStore<IngredientUnit>(store, loading, api.units);
}
