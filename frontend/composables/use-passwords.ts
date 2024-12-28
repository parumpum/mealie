import VueI18n from "vue-i18n";
import { Ref } from "vue";
import { computed, ref, useNuxtApp } from "#imports";
import { scorePassword } from "~/lib/validators";

export function usePasswordField() {
  const show = ref(false);
  const { $globals } = useNuxtApp();

  const passwordIcon = computed(() => {
    return show.value ? $globals.icons.eyeOff as string : $globals.icons.eye as string;
  });
  const inputType = computed(() => (show.value ? "text" : "password"));

  const togglePasswordShow = () => {
    show.value = !show.value;
  };

  return {
    inputType,
    togglePasswordShow,
    passwordIcon,
  };
}

export const usePasswordStrength = (password: Ref<string>, i18n: VueI18n) => {
  const score = computed(() => scorePassword(password.value));
  const strength = computed(() => {
    if (score.value < 50) {
      return String(i18n.tc("user.password-strength-values.weak"));
    } else if (score.value < 80) {
      return String(i18n.tc("user.password-strength-values.good"));
    } else if (score.value < 100) {
      return String(i18n.tc("user.password-strength-values.strong"));
    } else {
      return String(i18n.tc("user.password-strength-values.very-strong"));
    }
  });

  const color = computed(() => {
    if (score.value < 50) {
      return "error";
    } else if (score.value < 80) {
      return "warning";
    } else if (score.value < 100) {
      return "info";
    } else {
      return "success";
    }
  });

  return { score, strength, color };
};
