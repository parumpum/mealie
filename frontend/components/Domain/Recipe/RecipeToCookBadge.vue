<template>
  <v-tooltip bottom nudge-right="50" :color="buttonStyle ? 'info' : 'secondary'">
    <template #activator="{ on, attrs }">
      <v-btn
        v-if="isFlagged || showAlways"
        small
        :color="buttonStyle ? 'info' : 'secondary'"
        :icon="!buttonStyle"
        :fab="buttonStyle"
        v-bind="attrs"
        @click.prevent="toggleWantToCook"
        v-on="on"
      >
        <v-icon :small="false" :color="buttonStyle ? 'white' : 'secondary'">
          {{ isFlagged ? $globals.icons.bookmark : $globals.icons.bookmarkOutline }}
        </v-icon>
      </v-btn>
    </template>
    <span >{{ isFlagged ? $t("recipe.remove-from-wishlist") : $t("recipe.add-to-wishlist") }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import { useUserSelfRatings } from "~/composables/use-users";
import { useUserApi } from "~/composables/api";
import { UserOut } from "~/lib/api/types/user";
import { useLoggedInState } from "~/composables/use-logged-in-state";
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
    const { userRatings, refreshUserRatings, setRating } = useUserSelfRatings();
    const { isOwnGroup } = useLoggedInState();

    // TODO Setup the correct type for $auth.user
    // See https://github.com/nuxt-community/auth-module/issues/1097
    const user = computed(() => $auth.user as unknown as UserOut);

    const isFlagged = computed(() => {
      const rating = userRatings.value.find((r) => r.recipeId === props.recipeId);
      return rating?.isBookmarked || false;
    });

    async function toggleWantToCook() {
       if (!isFlagged.value) {
          await api.users.addBookmark(user.value?.id, props.recipeId);
       } else {
         await api.users.removeBookmark(user.value?.id, props.recipeId);
       }
       await refreshUserRatings();
    }

    return { isFlagged, toggleWantToCook };
  },
});
</script>
