<script setup>
import { computed } from 'vue'
import { CONTENT_TYPES, contentTypeMeta } from '../config/contentDraft'

const props = defineProps({
  contentType: { type: String, default: 'text_release' },
  title: { type: String, default: '' },
  body: { type: String, default: '' },
  mediaUrl: { type: String, default: '' },
})

const emit = defineEmits(['update:contentType', 'update:title', 'update:body', 'update:mediaUrl'])

const meta = computed(() => contentTypeMeta(props.contentType))
const fieldClass = 'mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm'
</script>

<template>
  <div class="md:col-span-2">
    <p class="text-sm font-medium text-banten-navy">Tipe produksi</p>
    <div class="mt-2 grid gap-2 sm:grid-cols-3">
      <button
        v-for="option in CONTENT_TYPES"
        :key="option.value"
        type="button"
        class="rounded-lg border px-3 py-2 text-left transition"
        :class="
          contentType === option.value
            ? 'border-banten-gold bg-amber-50/60'
            : 'border-banten-navy/15 hover:border-banten-gold/40'
        "
        @click="emit('update:contentType', option.value)"
      >
        <span class="block text-sm font-medium text-banten-navy">{{ option.label }}</span>
        <span class="mt-0.5 block text-xs text-banten-navy/60">{{ option.hint }}</span>
      </button>
    </div>
    <p class="mt-2 text-xs text-banten-navy/65">{{ meta.note }}</p>
  </div>

  <div :class="meta.mediaLabel ? '' : 'md:col-span-2'">
    <label class="text-sm font-medium text-banten-navy">{{ meta.titleLabel }}</label>
    <input
      :value="title"
      required
      :class="fieldClass"
      @input="emit('update:title', $event.target.value)"
    />
  </div>

  <div v-if="meta.mediaLabel">
    <label class="text-sm font-medium text-banten-navy">{{ meta.mediaLabel }}</label>
    <input
      :value="mediaUrl"
      type="url"
      :placeholder="meta.mediaPlaceholder"
      :class="fieldClass"
      @input="emit('update:mediaUrl', $event.target.value)"
    />
  </div>

  <div class="md:col-span-2">
    <label class="text-sm font-medium text-banten-navy">{{ meta.bodyLabel }}</label>
    <textarea
      :value="body"
      :rows="meta.bodyRows"
      :placeholder="meta.bodyPlaceholder"
      :required="contentType === 'text_release'"
      :class="fieldClass"
      @input="emit('update:body', $event.target.value)"
    />
  </div>
</template>
