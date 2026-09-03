<script setup>
import { RISK_LEVELS, riskMeta, riskTitle } from '../config/risk'

defineProps({
  compact: { type: Boolean, default: false },
})
</script>

<template>
  <ul
    class="grid gap-x-3 gap-y-1.5 text-banten-navy/75"
    :class="compact ? 'grid-cols-2 text-[11px] leading-snug' : 'grid-cols-2 sm:grid-cols-3 text-xs'"
  >
    <li
      v-for="code in RISK_LEVELS"
      :key="code"
      class="flex items-start gap-1.5"
      :title="riskTitle(code)"
    >
      <span
        class="mt-0.5 h-2.5 w-2.5 shrink-0 rounded-sm"
        :style="{ backgroundColor: riskMeta(code).chartColor }"
        aria-hidden="true"
      />
      <span>
        <span class="font-semibold text-banten-navy">{{ code }}</span>
        <span class="text-banten-navy/60"> — {{ riskMeta(code).short }}</span>
      </span>
    </li>
  </ul>
</template>
