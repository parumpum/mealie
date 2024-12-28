<template>
  <div>
    <RecipePage v-if="recipe" :recipe="recipe" />
  </div>
</template>

<script lang="ts">
import { whenever } from "@vueuse/core";
import { computed, defineComponent, ref, useLazyAsyncData, useNuxtApp, useNuxt2Meta, useRoute, useRouter } from "#imports";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useAsyncKey } from "~/composables/use-utils";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicExploreApi } from "~/composables/api/api-client";
import { useRecipe } from "~/composables/recipes";
import { Recipe } from "~/lib/api/types/recipe";

export default defineComponent({
  components: { RecipePage },
  setup() {
    const { $auth } = useNuxtApp();
    const { isOwnGroup } = useLoggedInState();
    const title = ref("Recipe");
    useNuxt2Meta({
      title,
    })
    const route = useRoute();
    const router = useRouter();
    const slug = route.params.slug;

    let recipe = ref<Recipe | null>(null);
    if (isOwnGroup.value) {
      const { recipe: data } = useRecipe(slug as string);
      recipe = data;
    } else {
      const groupSlug = computed(() => route.params.groupSlug as string || $auth.user?.groupSlug as string || "")
      const api = usePublicExploreApi(groupSlug.value);
      recipe = useLazyAsyncData(async () => {
        const { data, error } = await api.explore.recipes.getOne(slug as string);
        if (error) {
          console.error("error loading recipe -> ", error);
          router.push(`/g/${groupSlug.value}`);
        }

        return data;
      }, useAsyncKey())
    }

    whenever(
      () => recipe.value,
      () => {
        if (recipe.value && recipe.value.name) {
          title.value = recipe.value.name;
        }
      },
    )

    return {
      recipe,
    };
  },
  head: {},
});
</script>
