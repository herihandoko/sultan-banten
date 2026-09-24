<script setup>
import { computed, ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const open = ref(false)
const rootEl = ref(null)

onClickOutside(rootEl, () => {
  open.value = false
})

const displayName = computed(() => auth.user?.full_name || auth.user?.username || 'User')
const roleName = computed(() => auth.user?.role?.name || '—')

const initials = computed(() => {
  const name = displayName.value.trim()
  const parts = name.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase() || 'U'
})

async function onLogout() {
  open.value = false
  await auth.logout()
  window.location.assign('/login')
}
</script>

<template>
  <div ref="rootEl" class="relative">
    <button
      type="button"
      class="flex max-w-[11rem] items-center gap-2 rounded-lg border border-[#30363d] bg-[#161b22] p-1 text-left transition hover:border-emerald-500/40 sm:max-w-[16rem] sm:px-2.5 sm:py-1"
      :aria-expanded="open"
      aria-haspopup="menu"
      @click="open = !open"
    >
      <span
        class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-emerald-500/20 text-[11px] font-bold tracking-wide text-emerald-300"
        aria-hidden="true"
      >
        {{ initials }}
      </span>
      <span class="hidden min-w-0 flex-1 sm:block">
        <span class="block truncate text-xs font-semibold leading-tight text-white">
          {{ displayName }}
        </span>
        <span class="block truncate text-[10px] leading-tight text-[#8b949e]">
          {{ roleName }}
        </span>
      </span>
      <svg
        class="hidden h-3.5 w-3.5 shrink-0 text-[#8b949e] sm:block"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <div
      v-if="open"
      class="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-xl border border-[#30363d] bg-[#161b22] py-1 shadow-2xl"
      role="menu"
    >
      <div class="border-b border-[#30363d] px-3 py-2.5 sm:hidden">
        <p class="truncate text-xs font-semibold text-white">{{ displayName }}</p>
        <p class="truncate text-[10px] text-[#8b949e]">{{ roleName }}</p>
      </div>
      <button
        type="button"
        role="menuitem"
        class="flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-semibold text-[#c9d1d9] transition hover:bg-[#21262d] hover:text-rose-400"
        @click="onLogout"
      >
        <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6A2.25 2.25 0 0 0 5.25 5.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l3 3m0 0-3 3m3-3H9" />
        </svg>
        Keluar
      </button>
    </div>
  </div>
</template>
