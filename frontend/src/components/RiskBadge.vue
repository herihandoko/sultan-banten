<script setup>
import { computed } from 'vue'
import { riskMeta, riskTitle } from '../config/risk'

const props = defineProps({
  level: { type: String, default: 'R0' },
  showLabel: { type: Boolean, default: false },
  tone: { type: String, default: 'solid' },
})

const meta = computed(() => riskMeta(props.level))
const title = computed(() => riskTitle(props.level))
const toneClass = computed(() =>
  props.tone === 'outline' ? meta.value.outlineClass || meta.value.colorClass : meta.value.colorClass,
)
</script>

<template>
  <span
    class="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold"
    :class="toneClass"
    :title="title"
    :aria-label="title"
  >
    {{ meta.code }}
    <span v-if="showLabel" class="font-medium opacity-90">· {{ meta.short }}</span>
  </span>
</template>
