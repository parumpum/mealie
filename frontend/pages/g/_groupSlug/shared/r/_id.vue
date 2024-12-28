<template>
  <div>
    <client-only>
      <RecipePage v-if="recipe" :recipe="recipe" />
    </client-only>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useLazyAsyncData, useNuxtApp, useNuxt2Meta, useRoute, useRouter } from "#imports";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicApi } from "~/composables/api/api-client";

export default defineComponent({
  components: { RecipePage },
  layout: "basic",
  setup() {
    const { $auth } = useNuxtApp();
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user?.groupSlug as string || "");

    const router = useRouter();
    const recipeId = route.params.id;
    const api = usePublicApi();

    const title = ref("Recipe");
    useNuxt2Meta({
  title,
})
    const recipe = useLazyAsyncData(async () => {
      const { data, error } = await api.shared.getShared(recipeId as string);

      if (error) {
        console.error("error loading recipe -> ", error);
        router.push(`/g/${groupSlug.value}`);
      }

      if (data) {
        title.value = data?.name || "";
      }

      return data;
    });

    return {
      recipe,
    };
  },
  head: {},
});
</script>
