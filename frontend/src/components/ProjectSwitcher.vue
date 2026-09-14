<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useProjectStore } from '../stores/project'

const projectStore = useProjectStore()
const open = ref(false)
const rootEl = ref(null)

onClickOutside(rootEl, () => {
  open.value = false
})

const buttonLabel = computed(() => projectStore.label)

function selectProject(id) {
  projectStore.setSelectedId(id)
  open.value = false
}

onMounted(() => {
  projectStore.loadProjects()
})

let timer = null
onMounted(() => {
  timer = window.setInterval(() => {
    projectStore.loadProjects()
  }, 60_000)
})
onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div ref="rootEl" class="relative">
    <button
      type="button"
      class="inline-flex max-w-[11rem] items-center gap-1.5 rounded-lg border border-[#30363d] bg-[#161b22] px-2.5 py-1.5 text-xs font-semibold text-[#c9d1d9] transition hover:border-emerald-500/40 hover:text-white sm:max-w-[14rem]"
      :title="buttonLabel"
      :aria-expanded="open"
      aria-haspopup="listbox"
      @click="open = !open"
    >
      <span class="truncate">{{ buttonLabel }}</span>
      <svg
        class="h-3.5 w-3.5 shrink-0 text-[#8b949e]"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <div
      v-if="open"
      class="absolute right-0 z-50 mt-2 w-72 overflow-hidden rounded-xl border border-[#30363d] bg-[#161b22] py-2 shadow-2xl"
      role="listbox"
    >
      <div class="border-b border-[#30363d] px-3 pb-2">
        <p class="text-[11px] font-bold uppercase tracking-wider text-[#8b949e]">
          Project SIPANTAU
        </p>
        <p v-if="projectStore.loading" class="mt-1 text-[11px] text-[#6e7681]">Memuat…</p>
        <p v-else-if="projectStore.error" class="mt-1 text-[11px] text-rose-400">
          {{ projectStore.error }}
        </p>
      </div>

      <div class="max-h-64 overflow-y-auto">
        <button
          v-for="p in projectStore.projects"
          :key="p.id"
          type="button"
          role="option"
          class="flex w-full items-start gap-2 px-3 py-2 text-left transition hover:bg-[#21262d]"
          :class="projectStore.selectedId === p.id ? 'bg-[#21262d]/80' : ''"
          @click="selectProject(p.id)"
        >
          <span class="mt-0.5 text-sm">{{ p.avatar_emoji || '🏷️' }}</span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-xs font-semibold text-white">{{ p.name }}</span>
            <span class="block truncate text-[11px] text-[#8b949e]">{{ p.keyword }}</span>
          </span>
          <span
            v-if="projectStore.selectedId === p.id"
            class="mt-0.5 text-[10px] font-bold text-emerald-400"
          >✓</span>
        </button>

        <p
          v-if="!projectStore.loading && !projectStore.projects.length && !projectStore.error"
          class="px-3 py-3 text-[11px] text-[#8b949e]"
        >
          Belum ada project di SIPANTAU.
        </p>
      </div>
    </div>
  </div>
</template>
