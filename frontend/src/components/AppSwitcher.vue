<script setup>
import { computed } from 'vue'
import { APP_NAME } from '../config/app'
import { useNewsSourceStore } from '../stores/newsSource'

const newsSource = useNewsSourceStore()
const sipantauHref = '/sipantau/'
const showSipantau = computed(() => newsSource.showSipantauUi)
</script>

<template>
  <div
    class="inline-flex items-center rounded-xl border border-[#30363d] bg-[#161b22] p-0.5"
    role="navigation"
    aria-label="Pilih aplikasi"
  >
    <a
      v-if="showSipantau"
      :href="sipantauHref"
      class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-[#8b949e] transition hover:bg-[#21262d] hover:text-white"
      title="Buka SIPANTAU — Sistem Informasi Pantau (intel & listening, SSO)"
    >
      <svg class="h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M19.07 4.93A10 10 0 0 0 6.99 3.34" />
        <path d="M4 6h.01" />
        <path d="M2.29 9.62A10 10 0 1 0 21.31 8.35" />
        <path d="M16.24 7.76A6 6 0 1 0 8.23 16.67" />
        <path d="M12 18h.01" />
        <path d="M17.99 11.66A6 6 0 0 1 15.33 16.5" />
        <circle cx="12" cy="12" r="2" />
        <path d="m13.41 10.59 5.66-5.66" />
      </svg>
      SIPANTAU
    </a>
    <span
      class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500/15 px-2.5 py-1.5 text-xs font-bold text-emerald-400"
      aria-current="page"
      :title="`${APP_NAME} — respons krisis & media`"
    >
      <svg class="h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
      </svg>
      SIAGAPIM
    </span>
  </div>
</template>
