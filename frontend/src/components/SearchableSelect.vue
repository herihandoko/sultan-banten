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
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const root = ref(null)
const searchInput = ref(null)

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
      class="flex w-full items-center justify-between gap-2 rounded-md border border-banten-navy/20 bg-white px-3 py-2 text-left text-sm outline-none focus:border-banten-gold disabled:opacity-60"
      :disabled="disabled"
      :aria-expanded="open"
      aria-haspopup="listbox"
      @click="toggle"
    >
      <span class="truncate" :class="selected ? 'text-banten-navy' : 'text-banten-navy/45'">
        {{ selected?.label || placeholder }}
      </span>
      <svg
        class="h-4 w-4 shrink-0 text-banten-navy/45 transition"
        :class="open ? 'rotate-180' : ''"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="1.75"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <!-- Native required validation for form submit -->
    <input
      class="pointer-events-none absolute inset-0 h-0 w-0 opacity-0"
      tabindex="-1"
      :value="modelValue"
      :required="required"
      @focus="toggle"
    />

    <div
      v-if="open"
      class="absolute z-30 mt-1 w-full overflow-hidden rounded-md border border-banten-navy/15 bg-white shadow-lg"
      role="listbox"
    >
      <div class="border-b border-banten-navy/10 p-2">
        <input
          ref="searchInput"
          v-model="query"
          type="search"
          class="w-full rounded-md border border-banten-navy/20 px-3 py-1.5 text-sm outline-none focus:border-banten-gold"
          :placeholder="searchPlaceholder"
          @keydown.esc.stop="open = false"
        />
      </div>
      <ul class="max-h-56 overflow-y-auto py-1">
        <li>
          <button
            type="button"
            class="w-full px-3 py-2 text-left text-sm text-banten-navy/50 hover:bg-banten-sand/60"
            @click="clear"
          >
            {{ placeholder }}
          </button>
        </li>
        <li v-for="opt in filtered" :key="opt.value">
          <button
            type="button"
            class="w-full px-3 py-2 text-left text-sm hover:bg-banten-sand/60"
            :class="
              String(opt.value) === String(modelValue)
                ? 'bg-banten-navy/8 font-medium text-banten-navy'
                : 'text-banten-navy/80'
            "
            role="option"
            :aria-selected="String(opt.value) === String(modelValue)"
            @click="choose(opt)"
          >
            {{ opt.label }}
          </button>
        </li>
        <li v-if="!filtered.length" class="px-3 py-2 text-sm text-banten-navy/45">
          Tidak ada hasil
        </li>
      </ul>
    </div>
  </div>
</template>
