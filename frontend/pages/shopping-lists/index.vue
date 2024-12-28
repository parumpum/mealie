<template>
  <v-container v-if="shoppingListChoices && ready" class="narrow-container">
    <BaseDialog v-model="createDialog" :title="String($tc('shopping-list.create-shopping-list'))" @submit="createOne">
      <v-card-text>
        <v-text-field v-model="createName" autofocus :label="$t('shopping-list.new-list')"> </v-text-field>
      </v-card-text>
    </BaseDialog>

    <BaseDialog v-model="deleteDialog" :title="String($tc('general.confirm'))" color="error" @confirm="deleteOne">
      <v-card-text>{{ $t('shopping-list.are-you-sure-you-want-to-delete-this-item') }}</v-card-text>
    </BaseDialog>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/shopping-cart.svg')"></v-img>
      </template>
      <template #title>{{ $t('shopping-list.shopping-lists') }}</template>
    </BasePageTitle>

    <v-container class="d-flex justify-end px-0 pt-0 pb-4">
      <v-checkbox v-model="preferences.viewAllLists" hide-details :label="String($tc('general.show-all'))" class="my-auto mr-4" />
      <BaseButton create @click="createDialog = true" />
    </v-container>

    <section>
      <v-card
        v-for="list in shoppingListChoices"
        :key="list.id"
        class="my-2 left-border"
        :to="`/shopping-lists/${list.id}`"
      >
        <v-card-title>
          <v-icon left>
            {{ $globals.icons.cartCheck }}
          </v-icon>
          {{ list.name }}
          <v-btn class="ml-auto" icon @click.prevent="openDelete(list.id)">
            <v-icon>
              {{ $globals.icons.delete }}
            </v-icon>
          </v-btn>
        </v-card-title>
      </v-card>
    </section>
    <div class="d-flex justify-end mt-10">
      <ButtonLink :to="`/group/data/labels`" :text="String($tc('shopping-list.manage-labels'))" :icon="$globals.icons.tags" />
    </div>
  </v-container>
</template>

<script lang="ts">
import { Ref } from "vue";
import { computed, defineComponent, useLazyAsyncData, useNuxtApp, reactive, ref, toRefs, useRoute, useRouter, watch } from "#imports";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";
import { useShoppingListPreferences } from "~/composables/use-users/preferences";
import { ShoppingListOut } from "~/lib/api/types/household";

export default defineComponent({
  middleware: "auth",
  setup() {
    const { $auth } = useNuxtApp();
    const ready = ref(false);
    const userApi = useUserApi();
    const route = useRoute();
    const router = useRouter();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user?.groupSlug as string || "");
    const overrideDisableRedirect = ref(false);
    const disableRedirect = computed(() => route.query.disableRedirect === "true" || overrideDisableRedirect.value);
    const preferences = useShoppingListPreferences();

    const state = reactive({
      createName: "",
      createDialog: false,
      deleteDialog: false,
      deleteTarget: "",
    });

    const shoppingLists: Ref<ShoppingListOut[]> = ref(useLazyAsyncData(async () => {
      return await fetchShoppingLists();
    }, useAsyncKey()).data);


    const shoppingListChoices: Ref<ShoppingListOut[]> = ref([]);

    // This has to appear before the shoppingListChoices watcher, otherwise that runs first and the redirect is not disabled
    watch(
      () => preferences.value.viewAllLists,
      () => {
        overrideDisableRedirect.value = true;
      },
    );

    watch(
      () => shoppingLists,
      () => {
        console.log(shoppingLists.value);
        if (Array.isArray(shoppingLists.value)) {
          shoppingListChoices.value = shoppingLists.value.filter((list) => preferences.value.viewAllLists || list.userId === $auth.user?.id);
          ready.value = true;
        }
      },
      {
        deep: true,
      },
    );

    watch(
      () => shoppingListChoices,
      () => {
        if (!disableRedirect.value && shoppingListChoices.value.length === 1) {
          router.push(`/shopping-lists/${shoppingListChoices.value[0].id}`);
        } else {
          console.log("ready");
          ready.value = true;
        }
      },
      {
        deep: true,
      },
    );



    async function fetchShoppingLists() {
      const { data } = await userApi.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });

      if (!data) {
        return [];
      }

      return data.items;
    }

    async function refresh() {
      shoppingLists.value = await fetchShoppingLists();
    }

    async function createOne() {
      const { data } = await userApi.shopping.lists.createOne({ name: state.createName });

      if (data) {
        refresh();
        state.createName = "";
      }
    }

    function openDelete(id: string) {
      state.deleteDialog = true;
      state.deleteTarget = id;
    }

    async function deleteOne() {
      const { data } = await userApi.shopping.lists.deleteOne(state.deleteTarget);
      if (data) {
        refresh();
      }
    }

    return {
      ...toRefs(state),
      ready,
      groupSlug,
      preferences,
      shoppingListChoices,
      createOne,
      deleteOne,
      openDelete,
    };
  },
  head() {
    return {
      title: this.$t("shopping-list.shopping-list") as string,
    };
  },
});
</script>
