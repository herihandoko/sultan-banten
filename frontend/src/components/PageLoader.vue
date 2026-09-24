<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  done: { type: Boolean, default: false },
})

const emit = defineEmits(['finished'])

const percent = ref(0)
const gradId = `loader-${Math.random().toString(36).slice(2, 8)}`
const radius = 42
const circumference = 2 * Math.PI * radius

const offset = computed(() => circumference - (Math.min(100, percent.value) / 100) * circumference)
const shown = computed(() => Math.round(percent.value))
const stage = computed(() => {
  if (shown.value >= 100) return 'Siap ditampilkan'
  if (shown.value >= 70) return 'Merapikan tampilan'
  if (shown.value >= 35) return 'Menyusun angka'
  return 'Menghubungi sumber data'
})

let frame = 0
let startedAt = 0
let finished = false

function tick(now) {
  if (!startedAt) startedAt = now
  if (!props.done) {
    const elapsed = (now - startedAt) / 1000
    const eased = 92 * (1 - Math.exp(-elapsed / 0.85))
    percent.value = Math.max(percent.value, Math.min(92, eased))
  } else {
    percent.value = Math.min(100, percent.value + Math.max(1.8, (100 - percent.value) * 0.22))
    if (percent.value >= 99.6 && !finished) {
      percent.value = 100
      finished = true
      window.setTimeout(() => emit('finished'), 280)
      return
    }
  }
  frame = window.requestAnimationFrame(tick)
}

watch(
  () => props.done,
  (done) => {
    if (done && percent.value < 8) percent.value = 8
  },
)

onMounted(() => {
  frame = window.requestAnimationFrame(tick)
})

onUnmounted(() => {
  if (frame) window.cancelAnimationFrame(frame)
})
</script>

<template>
  <div class="flex min-h-[24rem] items-center justify-center py-8">
    <div class="w-full max-w-sm rounded-2xl border border-[#30363d] bg-[#161b22] px-8 py-9 text-center">
      <div class="relative mx-auto h-32 w-32">
        <svg class="h-full w-full -rotate-90" viewBox="0 0 100 100" aria-hidden="true">
          <circle cx="50" cy="50" r="42" fill="none" stroke="#30363d" stroke-width="6" />
          <circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            :stroke="`url(#${gradId})`"
            stroke-width="6"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="offset"
          />
          <defs>
            <linearGradient :id="gradId" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#34d399" />
              <stop offset="100%" stop-color="#38bdf8" />
            </linearGradient>
          </defs>
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center">
          <span class="text-3xl font-semibold tabular-nums tracking-tight text-white">{{ shown }}</span>
          <span class="text-[11px] font-semibold text-[#8b949e]">%</span>
        </div>
      </div>

      <p class="mt-6 text-sm font-semibold text-white">{{ title }}</p>
      <p class="mt-1 flex items-center justify-center gap-2 text-xs text-[#8b949e]">
        {{ stage }}
        <span class="inline-flex gap-1" aria-hidden="true">
          <span class="h-1 w-1 animate-bounce rounded-full bg-emerald-300 [animation-delay:0ms]" />
          <span class="h-1 w-1 animate-bounce rounded-full bg-emerald-300 [animation-delay:120ms]" />
          <span class="h-1 w-1 animate-bounce rounded-full bg-emerald-300 [animation-delay:240ms]" />
        </span>
      </p>

      <div class="mt-5 h-1.5 overflow-hidden rounded-full bg-[#0d1117]">
        <div
          class="h-full rounded-full bg-gradient-to-r from-emerald-400 to-sky-400"
          :style="{ width: `${shown}%` }"
        />
      </div>
    </div>
  </div>
</template>
