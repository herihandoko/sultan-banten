<script setup>
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { usePeriodStore } from '../stores/period'

const periodStore = usePeriodStore()
const open = ref(false)
const rootEl = ref(null)

onClickOutside(rootEl, () => {
  open.value = false
})

function select(value) {
  periodStore.setPeriod(value)
  open.value = false
}
</script>

<template>
  <div ref="rootEl" class="relative">
    <button
      type="button"
      class="flex items-center gap-1.5 rounded-lg border border-[#30363d] bg-[#161b22] px-2.5 py-1.5 text-xs font-semibold text-white transition hover:border-emerald-500/40"
      :aria-expanded="open"
      aria-haspopup="listbox"
      title="Periode analisis (Asia/Jakarta)"
      @click="open = !open"
    >
      <svg class="h-3.5 w-3.5 shrink-0 text-[#8b949e]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3.75 8.25h16.5M4.5 6.75h15A1.5 1.5 0 0 1 21 8.25v11.25A1.5 1.5 0 0 1 19.5 21h-15A1.5 1.5 0 0 1 3 19.5V8.25A1.5 1.5 0 0 1 4.5 6.75Z" />
      </svg>
      <span class="max-w-[7.5rem] truncate sm:max-w-none">{{ periodStore.label }}</span>
      <svg class="h-3.5 w-3.5 shrink-0 text-[#8b949e]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <div
      v-if="open"
      class="absolute right-0 z-50 mt-2 w-64 overflow-hidden rounded-xl border border-[#30363d] bg-[#161b22] py-2 shadow-2xl"
      role="listbox"
    >
      <div class="border-b border-[#30363d] px-3 pb-2">
        <p class="text-[11px] font-bold uppercase tracking-wider text-[#8b949e]">
          Periode analisis
        </p>
        <p class="mt-0.5 text-[10px] text-[#6e7681]">Asia/Jakarta</p>
      </div>
      <button
        v-for="opt in periodStore.options"
        :key="opt.value"
        type="button"
        role="option"
        class="flex w-full flex-col gap-0.5 px-3 py-2 text-left transition hover:bg-[#21262d]"
        :class="periodStore.period === opt.value ? 'bg-[#21262d]/80' : ''"
        @click="select(opt.value)"
      >
        <span class="flex items-center justify-between gap-2">
          <span class="text-xs font-semibold text-white">{{ opt.label }}</span>
          <span
            v-if="periodStore.period === opt.value"
            class="text-[10px] font-bold text-emerald-400"
          >✓</span>
        </span>
        <span class="text-[10px] text-[#8b949e]">{{ opt.periodText }}</span>
      </button>
    </div>
  </div>
</template>
