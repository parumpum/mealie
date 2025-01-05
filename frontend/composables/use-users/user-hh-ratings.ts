import { ref, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { UserRatingSummary } from "~/lib/api/types/user";

const householdBookmarks = ref<UserRatingSummary[]>([]);
const loading = ref(false);
const ready = ref(false);

export const useHouseholdBookmarks = function () {
  const { $auth } = useContext();
  const api = useUserApi();

  async function refreshHouseholdBookmarks() {
    if (!$auth.user || loading.value) {
      return;
    }

    loading.value = true;
    const { data } = await api.users.getHouseholdBookmarks();
    householdBookmarks.value = data?.ratings || [];
    loading.value = false;
    ready.value = true;
  }

  async function setRating(slug: string, rating: number | null, isFavorite: boolean | null, isBookmarked: boolean | null) {
    loading.value = true;
    const userId = $auth.user?.id || "";
    await api.users.setRating(userId, slug, rating, isFavorite, isBookmarked);
    loading.value = false;
    await refreshHouseholdBookmarks();
  }

  if (!ready.value) {
    refreshHouseholdBookmarks();
  }

  return {
    householdBookmarks,
    refreshHouseholdBookmarks,
    setRating,
    ready,
  }
}
