<template>
  <div scoped-slot></div>
</template>

<script lang="ts">
import { defineComponent, useNuxtApp } from "#imports";

/**
 * Renderless component that only renders if the user is logged in.
 * and has advanced options toggled.
 */
export default defineComponent({
  setup(_, ctx) {
    const { $auth } = useNuxtApp();

    const r = $auth?.user?.advanced || false;

    return () => {
      return r ? ctx.slots.default?.() : null;
    };
  },
});
</script>
