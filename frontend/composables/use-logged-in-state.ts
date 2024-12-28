import { computed, useNuxtApp, useRoute } from "#imports";

export const useLoggedInState = function () {
  const { $auth }: { $auth: { loggedIn: boolean, user?: { groupSlug?: string } } } = useNuxtApp();
  const route = useRoute();

  const loggedIn = computed<boolean>(() => $auth.loggedIn);
  const isOwnGroup = computed(() => {
    if (!route.params.groupSlug) {
      return loggedIn.value;
    } else {
      return loggedIn.value && $auth.user?.groupSlug === route.params.groupSlug;
    }
  });

  return { loggedIn, isOwnGroup };
}
