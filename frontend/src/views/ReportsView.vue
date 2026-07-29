<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const types = ref([])
const loading = ref(true)
const error = ref('')
const busy = ref('')
const issueId = ref('')

const role = computed(() => auth.user?.role?.code)

const visibleTypes = computed(() => {
  if (role.value === 'media_kol_admin') {
    return types.value.filter((t) => ['media_sla', 'kol'].includes(t.code))
  }
  return types.value
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/reports/types')
    types.value = data.data || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat jenis laporan'
  } finally {
    loading.value = false
  }
}

async function download(code, format) {
  const key = `${code}-${format}`
  busy.value = key
  error.value = ''
  try {
    const params = { format }
    if (code === 'crisis' && issueId.value) params.issue_id = issueId.value
    const res = await api.get(`/reports/export/${code}`, {
      params,
      responseType: 'blob',
    })
    const disposition = res.headers['content-disposition'] || ''
    const match = disposition.match(/filename="?([^"]+)"?/)
    const filename = match?.[1] || `laporan-${code}.${format === 'xlsx' ? 'xlsx' : 'pdf'}`
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    // blob error body
    let msg = 'Gagal mengunduh laporan'
    try {
      const text = await err.response?.data?.text?.()
      if (text) msg = JSON.parse(text).error || msg
    } catch {
      /* ignore */
    }
    error.value = msg
  } finally {
    busy.value = ''
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="font-display text-3xl text-banten-navy">Laporan &amp; Export</h1>
      <p class="mt-1 text-sm text-banten-navy/65">
        PRD §9.1 — unduh PDF / Excel untuk krisis, SLA media, ASN, KOL, dan executive brief
      </p>
    </div>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="mb-4 rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <div class="mb-5 rounded-xl border border-banten-navy/10 bg-white/90 p-4">
      <label class="text-sm font-medium text-banten-navy">Filter isu (opsional, untuk laporan krisis)</label>
      <input
        v-model="issueId"
        type="number"
        min="1"
        placeholder="ID isu"
        class="mt-1 w-full max-w-xs rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
      />
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <article
        v-for="t in visibleTypes"
        :key="t.code"
        class="rounded-xl border border-banten-navy/10 bg-white/90 p-5"
      >
        <h2 class="font-display text-xl text-banten-navy">{{ t.name }}</h2>
        <p class="mt-1 text-xs uppercase tracking-wide text-banten-navy/45">{{ t.code }}</p>
        <div class="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white disabled:opacity-60"
            :disabled="busy === `${t.code}-pdf`"
            @click="download(t.code, 'pdf')"
          >
            {{ busy === `${t.code}-pdf` ? '...' : 'PDF' }}
          </button>
          <button
            type="button"
            class="rounded-md border border-banten-navy/20 px-3 py-2 text-xs text-banten-navy hover:bg-banten-sand disabled:opacity-60"
            :disabled="busy === `${t.code}-xlsx`"
            @click="download(t.code, 'xlsx')"
          >
            {{ busy === `${t.code}-xlsx` ? '...' : 'Excel' }}
          </button>
        </div>
      </article>
    </div>
  </div>
</template>
