<script setup>
defineProps({
  title: { type: String, required: true },
  code: { type: String, default: '' },
})
</script>

<template>
  <div class="rounded-xl border border-dashed border-banten-navy/20 bg-white/60 px-6 py-16 text-center">
    <p v-if="code" class="text-xs font-semibold tracking-wider text-banten-gold uppercase">{{ code }}</p>
    <h1 class="mt-2 font-display text-3xl text-banten-navy">{{ title }}</h1>
    <p class="mt-3 text-sm text-banten-navy/60">Modul ini akan dikembangkan pada milestone berikutnya.</p>
  </div>
</template>
