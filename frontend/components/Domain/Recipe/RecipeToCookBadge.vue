<template>
  <v-tooltip bottom nudge-right="50" :color="buttonStyle ? 'info' : 'secondary'">
    <template #activator="{ on, attrs }">
      <v-btn
        v-bind="attrs"
        :class="buttonStyle ? 'mr-1' : ''"
        small
        :color="buttonStyle ? 'info' : 'secondary'"
        :icon="!buttonStyle"
        :fab="buttonStyle"
        @click.prevent="toggleWantToCook"
        v-on="on"
      >
        <v-icon :key="componentKey" :small="false" :color="isFlagged ? 'secondary' : 'grey darken-1'">
          {{ isFlagged ? $globals.icons.bookmark : isHouseholdFlagged ? $globals.icons.bookmark : $globals.icons.bookmarkOutline }}
        </v-icon>
      </v-btn>
    </template>
    <span >{{ isFlagged ? $t("recipe.remove-from-wishlist") : $t("recipe.add-to-wishlist") }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref, useContext } from "@nuxtjs/composition-api";
import { useUserSelfRatings } from "~/composables/use-users";
import { useUserApi } from "~/composables/api";
import { UserOut } from "~/lib/api/types/user";
import { useHouseholdBookmarks } from "~/composables/use-users/user-hh-ratings";

export default defineComponent({
  props: {
    recipeId: {
      type: String,
      default: "",
    },
    slug: {
      type: String,
      default: "",
    },
    showAlways: {
      type: Boolean,
      default: false,
    },
    buttonStyle: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const api = useUserApi();
    const { $auth } = useContext();
    const { userRatings, refreshUserRatings } = useUserSelfRatings();
    const { householdBookmarks } = useHouseholdBookmarks();

    // const ready = ref(false);
    const componentKey = ref(0);
    // TODO Setup the correct type for $auth.user
    // See https://github.com/nuxt-community/auth-module/issues/1097
    const user = computed(() => $auth.user as unknown as UserOut);
    // const isHouseholdFlagged = ref(false)

    function forceRerender() {
      componentKey.value += 1;
    }

    const isFlagged = computed(() => {
      const rating = userRatings.value.find((r) => r.recipeId === props.recipeId);
      if (rating?.isBookmarked) {
        return true;
      }
      return false;
    });

    const isHouseholdFlagged = computed(() => {
      const rating = householdBookmarks.value.find((r) => r.recipeId === props.recipeId);
      if (rating?.isBookmarked) {
        return true;
      }
      return false;
    });


    // onMounted(async () => {
    //   await checkHouseholdFlagged();
    //   ready.value = true;
    // });

    //  async function checkHouseholdFlagged() {
    //   if (!$auth.user) {
    //     return;
    //   }

    //   const rating = await api.users.getHouseholdBookmarksByRecipe($auth.user.id, props.recipeId);
    //   if (rating && rating.data) {
    //       isHouseholdFlagged.value = true;
    //       forceRerender();

    //   } else {
    //       isHouseholdFlagged.value = false;
    //     }

    // }

    async function toggleWantToCook() {
       if (!isFlagged.value) {
          await api.users.addBookmark(user.value?.id, props.recipeId);
       } else {
         await api.users.removeBookmark(user.value?.id, props.recipeId);
       }
       await refreshUserRatings();
       // await refreshHouseholdBookmarks();
       forceRerender();
    }

    return { isFlagged, toggleWantToCook, isHouseholdFlagged, componentKey };
  },
});
</script>
