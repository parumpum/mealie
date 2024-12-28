import { Ref } from "vue";
import { useAsyncKey } from "../use-utils";
import { ref, useLazyAsyncData, useNuxtApp } from "#imports";
import { AppInfo } from "~/lib/api/types/admin";

export function useAppInfo(): Ref<AppInfo | null> {
  const appInfo = ref<null | AppInfo>(null);

  const { $axios, $i18n } = useNuxtApp();
  $axios.setHeader("Accept-Language", $i18n.locale);

  useLazyAsyncData(async () => {
    const data = await $axios.get<AppInfo>("/api/app/about");
    appInfo.value = data.data;
  }, useAsyncKey());

  return appInfo;
}
