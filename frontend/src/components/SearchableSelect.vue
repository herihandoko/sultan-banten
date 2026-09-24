<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { onClickOutside } from '@vueuse/core'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '— pilih —' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  searchPlaceholder: { type: String, default: 'Cari...' },
  /** light | dark — use hex colors so html.dark overrides don't wash out contrast */
  tone: { type: String, default: 'light' },
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const root = ref(null)
const searchInput = ref(null)

const dark = computed(() => props.tone === 'dark')

onClickOutside(root, () => {
  open.value = false
})

const selected = computed(() =>
  props.options.find((o) => String(o.value) === String(props.modelValue)),
)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return props.options
  return props.options.filter((o) => String(o.label).toLowerCase().includes(q))
})

watch(open, async (isOpen) => {
  if (isOpen) {
    query.value = ''
    await nextTick()
    searchInput.value?.focus()
  }
})

function toggle() {
  if (props.disabled) return
  open.value = !open.value
}

function choose(option) {
  emit('update:modelValue', option.value)
  open.value = false
}

function clear() {
  emit('update:modelValue', '')
  open.value = false
}
</script>

<template>
  <div ref="root" class="relative mt-1">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-2 rounded-lg border px-3 py-2 text-left text-sm outline-none transition disabled:opacity-60"
      :class="
        dark
          ? 'border-[#30363d] bg-[#0d1117] text-[#e6edf3] focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'
          : 'border-[#cbd5e1] bg-white text-[#1b3a5c] focus:border-[#c9a227]'
      "
      :disabled="disabled"
      :aria-expanded="open"
      aria-haspopup="listbox"
      @click="toggle"
    >
      <span
        class="truncate"
        :class="selected ? (dark ? 'text-[#e6edf3]' : 'text-[#1b3a5c]') : dark ? 'text-[#6e7681]' : 'text-[#64748b]'"
      >
        {{ selected?.label || placeholder }}
      </span>
      <svg
        class="h-4 w-4 shrink-0 transition"
        :class="[open ? 'rotate-180' : '', dark ? 'text-[#8b949e]' : 'text-[#94a3b8]']"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="1.75"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <input
      class="pointer-events-none absolute inset-0 h-0 w-0 opacity-0"
      tabindex="-1"
      :value="modelValue"
      :required="required"
      @focus="toggle"
    />

    <div
      v-if="open"
      class="absolute z-30 mt-1 w-full overflow-hidden rounded-xl border shadow-2xl"
      :class="dark ? 'border-[#30363d] bg-[#161b22]' : 'border-[#e2e8f0] bg-white'"
      role="listbox"
    >
      <div class="border-b p-2" :class="dark ? 'border-[#30363d]' : 'border-[#e2e8f0]'">
        <input
          ref="searchInput"
          v-model="query"
          type="search"
          class="w-full rounded-lg border px-3 py-1.5 text-sm outline-none"
          :class="
            dark
              ? 'border-[#30363d] bg-[#0d1117] text-[#e6edf3] placeholder:text-[#6e7681] focus:border-emerald-500/50'
              : 'border-[#cbd5e1] bg-white text-[#1b3a5c] placeholder:text-[#94a3b8] focus:border-[#c9a227]'
          "
          :placeholder="searchPlaceholder"
          @keydown.esc.stop="open = false"
        />
      </div>
      <ul class="max-h-56 overflow-y-auto py-1">
        <li>
          <button
            type="button"
            class="w-full px-3 py-2 text-left text-sm transition"
            :class="dark ? 'text-[#6e7681] hover:bg-[#21262d]' : 'text-[#64748b] hover:bg-[#f1f5f9]'"
            @click="clear"
          >
            {{ placeholder }}
          </button>
        </li>
        <li v-for="opt in filtered" :key="opt.value">
          <button
            type="button"
            class="w-full px-3 py-2 text-left text-sm transition"
            :class="
              String(opt.value) === String(modelValue)
                ? dark
                  ? 'bg-[#21262d] font-medium text-emerald-300'
                  : 'bg-[#e8eef4] font-medium text-[#1b3a5c]'
                : dark
                  ? 'text-[#c9d1d9] hover:bg-[#21262d]'
                  : 'text-[#1b3a5c] hover:bg-[#f1f5f9]'
            "
            role="option"
            :aria-selected="String(opt.value) === String(modelValue)"
            @click="choose(opt)"
          >
            {{ opt.label }}
          </button>
        </li>
        <li
          v-if="!filtered.length"
          class="px-3 py-2 text-sm"
          :class="dark ? 'text-[#6e7681]' : 'text-[#94a3b8]'"
        >
          Tidak ada hasil
        </li>
      </ul>
    </div>
  </div>
</template>
