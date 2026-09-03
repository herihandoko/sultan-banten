<script setup>
import { computed } from 'vue'
import { issueStatusMeta, issueStatusTitle } from '../config/issueStatus'

const props = defineProps({
  status: { type: String, default: '' },
  showDescription: { type: Boolean, default: false },
})

const meta = computed(() => issueStatusMeta(props.status))
const title = computed(() => issueStatusTitle(props.status))
</script>

<template>
  <span
    class="inline-flex max-w-full items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium"
    :class="meta.colorClass"
    :title="title"
    :aria-label="title"
  >
    {{ meta.short }}
    <span v-if="showDescription" class="font-normal opacity-80">· {{ meta.description }}</span>
  </span>
</template>
