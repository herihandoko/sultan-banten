import { computed, watch } from 'vue'
import { defineStore } from 'pinia'
import { useLocalStorage } from '@vueuse/core'

function applyDomTheme(mode) {
  const root = document.documentElement
  if (mode === 'dark') {
    root.classList.add('dark')
    root.style.colorScheme = 'dark'
  } else {
    root.classList.remove('dark')
    root.style.colorScheme = 'light'
  }
}

export const useThemeStore = defineStore('theme', () => {
  /** @type {import('vue').Ref<'light' | 'dark'>} */
  const mode = useLocalStorage('sb-theme', 'dark')
  const isDark = computed(() => mode.value === 'dark')

  function setMode(next) {
    mode.value = next === 'light' ? 'light' : 'dark'
  }

  function toggle() {
    setMode(mode.value === 'dark' ? 'light' : 'dark')
  }

  watch(
    mode,
    (m) => applyDomTheme(m),
    { immediate: true },
  )

  return {
    mode,
    isDark,
    setMode,
    toggle,
  }
})
