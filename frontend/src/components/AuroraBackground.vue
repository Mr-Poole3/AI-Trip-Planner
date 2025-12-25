<script setup lang="ts">
import { computed } from "vue";

interface Props {
  class?: string;
  showRadialGradient?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showRadialGradient: true,
});

const computedClass = computed(() => {
  return props.class || "";
});
</script>

<template>
  <div class="relative flex flex-col h-[100vh] items-center justify-center bg-white text-slate-950 transition-bg" :class="computedClass">
    <div class="absolute inset-0 overflow-hidden">
      <div
        class="
          [--white-gradient:repeating-linear-gradient(100deg,var(--white)_0%,var(--white)_7%,var(--transparent)_10%,var(--transparent)_12%,var(--white)_16%)]
          [--aurora:repeating-linear-gradient(100deg,#3b82f6_10%,#a855f7_15%,#9333ea_20%,#2563eb_30%,#3b82f6_40%)]
          [background-image:var(--white-gradient),var(--aurora)]
          [background-size:300%,_200%]
          [background-position:50%_50%,50%_50%]
          filter blur-[10px] invert
          after:content-[''] after:absolute after:inset-0 after:[background-image:var(--white-gradient),var(--aurora)]
          after:[background-size:200%,_100%]
          after:animate-aurora after:[background-attachment:fixed] after:mix-blend-difference
          pointer-events-none
          absolute -inset-[10px] opacity-30
          will-change-transform
        "
      ></div>
    </div>
    <div class="relative z-10 w-full flex flex-col items-center justify-center">
        <slot />
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles can be empty if variables are global */
</style>
