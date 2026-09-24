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

const REPORT_META = {
  crisis: {
    hint: 'Kronologi isu, validasi OPD, naskah klarifikasi, dan keputusan pimpinan.',
    accent: 'from-rose-500/80',
  },
  media_sla: {
    hint: 'Kepatuhan mitra media terhadap target waktu tayang dan riwayat blast.',
    accent: 'from-sky-500/80',
  },
  asn: {
    hint: 'Jumlah partisipasi ASN per OPD pada mission board.',
    accent: 'from-emerald-500/80',
  },
  kol: {
    hint: 'Kontrak, campaign, dan metrik tayangan key opinion leader.',
    accent: 'from-violet-500/80',
  },
  executive: {
    hint: 'Ringkasan untuk pimpinan: isu aktif, tingkat risiko, dan progres penanganan.',
    accent: 'from-amber-400/80',
  },
}

function reportMeta(code) {
  return REPORT_META[code] || {
    hint: 'Unduh rekap dalam PDF atau Excel.',
    accent: 'from-slate-400/80',
  }
}
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

    <div class="grid gap-4 md:grid-cols-2">
      <article
        v-for="t in visibleTypes"
        :key="t.code"
        class="relative flex flex-col overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
      >
        <div
          class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent"
          :class="reportMeta(t.code).accent"
          aria-hidden="true"
        />
        <div class="px-5 py-4 pl-6">
          <div class="flex items-start justify-between gap-3">
            <h2 class="text-base font-semibold leading-snug text-white sm:text-lg">{{ t.name }}</h2>
            <span class="shrink-0 rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-[#8b949e]">
              {{ t.code }}
            </span>
          </div>
          <p class="mt-2 text-sm leading-relaxed text-[#8b949e]">{{ reportMeta(t.code).hint }}</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="fmt in t.formats || ['pdf', 'xlsx']"
              :key="fmt"
              class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold uppercase text-[#c9d1d9]"
            >
              {{ fmt }}
            </span>
          </div>
          <label v-if="t.code === 'crisis'" class="mt-4 block text-[11px] font-medium text-[#8b949e]">
            Batasi ke satu isu (opsional)
            <input
              v-model="issueId"
              type="number"
              min="1"
              placeholder="ID isu"
              class="mt-1 w-full max-w-xs rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#e6edf3] outline-none placeholder:text-[#6e7681] focus:border-emerald-500/50"
            />
          </label>
        </div>
        <div class="mt-auto flex gap-4 border-t border-[#30363d]/80 px-5 py-2.5 pl-6 text-xs font-semibold">
          <button
            type="button"
            class="text-emerald-300 hover:text-emerald-200 disabled:opacity-60"
            :disabled="busy === `${t.code}-pdf`"
            @click="download(t.code, 'pdf')"
          >
            {{ busy === `${t.code}-pdf` ? 'Menyiapkan PDF...' : 'Unduh PDF' }}
          </button>
          <button
            type="button"
            class="text-sky-300 hover:text-sky-200 disabled:opacity-60"
            :disabled="busy === `${t.code}-xlsx`"
            @click="download(t.code, 'xlsx')"
          >
            {{ busy === `${t.code}-xlsx` ? 'Menyiapkan Excel...' : 'Unduh Excel' }}
          </button>
        </div>
      </article>
    </div>
  </div>
</template>
