<template>
  <div>
    <RecipeExplorerPage />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "#imports";
import RecipeExplorerPage from "~/components/Domain/Recipe/RecipeExplorerPage.vue";

export default defineComponent({
  components: { RecipeExplorerPage },
});
</script>
