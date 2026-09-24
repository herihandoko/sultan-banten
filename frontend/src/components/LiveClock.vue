<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const clockText = ref('—.—')
let timer = null

function formatWibTime(date = new Date()) {
  return date.toLocaleTimeString('id-ID', {
    timeZone: 'Asia/Jakarta',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function tick() {
  clockText.value = formatWibTime()
}

onMounted(() => {
  tick()
  timer = window.setInterval(tick, 10_000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div
    class="hidden items-center gap-1.5 rounded-lg border border-[#30363d] bg-[#161b22] px-2.5 py-1.5 font-mono text-[11px] text-[#c9d1d9] md:flex"
    title="Waktu Asia/Jakarta"
  >
    <span class="tabular-nums tracking-wide">{{ clockText }}</span>
    <span class="text-[#8b949e]">WIB</span>
    <span class="inline-flex items-center gap-1 font-sans text-[10px] font-bold uppercase tracking-wider text-emerald-400">
      <span class="relative flex h-1.5 w-1.5">
        <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
        <span class="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
      </span>
      Live
    </span>
  </div>
</template>
