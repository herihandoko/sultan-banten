<script setup>
import { computed } from 'vue'
import { riskMeta, riskTitle } from '../config/risk'

const props = defineProps({
  level: { type: String, default: 'R0' },
  showLabel: { type: Boolean, default: false },
})

const meta = computed(() => riskMeta(props.level))
const title = computed(() => riskTitle(props.level))
</script>

<template>
  <span
    class="inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-semibold"
    :class="meta.colorClass"
    :title="title"
    :aria-label="title"
  >
    {{ meta.code }}
    <span v-if="showLabel" class="font-medium opacity-90">· {{ meta.short }}</span>
  </span>
</template>
