<script setup>
import { computed } from 'vue'
import { issueStatusMeta, issueStatusTitle } from '../config/issueStatus'

const props = defineProps({
  status: { type: String, default: '' },
  showDescription: { type: Boolean, default: false },
  tone: { type: String, default: 'solid' },
})

const meta = computed(() => issueStatusMeta(props.status))
const title = computed(() => issueStatusTitle(props.status))
const toneClass = computed(() =>
  props.tone === 'outline' ? meta.value.outlineClass || meta.value.colorClass : meta.value.colorClass,
)
</script>

<template>
  <span
    class="inline-flex max-w-full items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium"
    :class="toneClass"
    :title="title"
    :aria-label="title"
  >
    {{ meta.short }}
    <span v-if="showDescription" class="font-normal opacity-80">· {{ meta.description }}</span>
  </span>
</template>
