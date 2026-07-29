<script setup>
defineProps({
  meta: {
    type: Object,
    default: () => ({
      page: 1,
      per_page: 10,
      total: 0,
      pages: 0,
      has_next: false,
      has_prev: false,
    }),
  },
})

const emit = defineEmits(['update:page'])

function go(page) {
  if (page < 1) return
  emit('update:page', page)
}
</script>

<template>
  <div
    v-if="meta && meta.total > 0"
    class="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-banten-navy/10 pt-4 text-sm"
  >
    <p class="text-banten-navy/55">
      Menampilkan
      <span class="font-medium text-banten-navy">
        {{ (meta.page - 1) * meta.per_page + 1 }}–{{ Math.min(meta.page * meta.per_page, meta.total) }}
      </span>
      dari
      <span class="font-medium text-banten-navy">{{ meta.total }}</span>
    </p>
    <div class="flex items-center gap-1">
      <button
        type="button"
        class="rounded-md border border-banten-navy/15 px-2.5 py-1.5 text-banten-navy disabled:opacity-40"
        :disabled="!meta.has_prev"
        @click="go(meta.page - 1)"
      >
        ‹ Prev
      </button>
      <span class="min-w-20 px-2 text-center text-banten-navy/70">
        {{ meta.page }} / {{ meta.pages || 1 }}
      </span>
      <button
        type="button"
        class="rounded-md border border-banten-navy/15 px-2.5 py-1.5 text-banten-navy disabled:opacity-40"
        :disabled="!meta.has_next"
        @click="go(meta.page + 1)"
      >
        Next ›
      </button>
    </div>
  </div>
</template>
