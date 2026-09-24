<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { usePeriodStore } from '../stores/period'
import { useProjectStore } from '../stores/project'
import RiskBadge from '../components/RiskBadge.vue'
import IssueStatusBadge from '../components/IssueStatusBadge.vue'
import { RISK_LEVELS, RISK_META, riskOptionLabel, riskTitle } from '../config/risk'
import { ISSUE_STATUSES, issueStatusMeta, issueStatusOptionLabel } from '../config/issueStatus'

const auth = useAuthStore()
const projectStore = useProjectStore()
const periodStore = usePeriodStore()
const issues = ref([])
const meta = ref(null)
const page = ref(1)
const loading = ref(true)
const error = ref('')
const showCreate = ref(false)
const creating = ref(false)
const createError = ref('')
const filters = ref({
  q: '',
  status: '',
  risk_level: '',
  sort_by: 'created_at',
  sort_dir: 'desc',
})
const syncInfo = ref(null)
const summary = ref({
  open: 0,
  elevated: 0,
  by_risk: { R0: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0 },
})
const form = ref({
  title: '',
  summary: '',
  why_now: '',
  risk_level: 'R2',
})

const sortOptions = [
  { value: 'created_at', label: 'Waktu dibuat' },
  { value: 'updated_at', label: 'Terakhir update' },
  { value: 'risk_level', label: 'Risk level' },
  { value: 'status', label: 'Status' },
  { value: 'title', label: 'Judul' },
]

const canCreate = computed(() => {
  const code = auth.user?.role?.code
  return code === 'super_admin' || code === 'editor'
})

const canDelete = computed(() => canCreate.value)

const pdfBusyId = ref(null)
const deletingId = ref(null)
const actionError = ref('')

const totalIssues = computed(() => meta.value?.total || 0)

const riskCards = computed(() =>
  RISK_LEVELS.map((level) => {
    const meta = RISK_META[level] || RISK_META.R0
    return {
      level,
      label: level,
      short: meta.short,
      description: meta.description,
      count: summary.value?.by_risk?.[level] || 0,
      title: riskTitle(level),
    }
  }),
)

const activeFilterCount = computed(() => {
  let n = 0
  if (filters.value.q) n += 1
  if (filters.value.status) n += 1
  if (filters.value.risk_level) n += 1
  return n
})

const hasActiveFilters = computed(() => activeFilterCount.value > 0)

const inputClass =
  'mt-1 w-full rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#e6edf3] placeholder:text-[#6e7681] outline-none transition focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'

const filterControlClass =
  'w-full appearance-none rounded-xl border border-[#30363d] bg-[#0d1117] py-2.5 pl-3 pr-8 text-sm text-[#e6edf3] outline-none transition hover:border-[#484f58] focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'

const RISK_ACCENT = {
  R0: 'from-slate-500/80',
  R1: 'from-sky-500/80',
  R2: 'from-amber-400/80',
  R3: 'from-orange-500/80',
  R4: 'from-rose-500/80',
  R5: 'from-red-500',
}

const RISK_CARD_CLASS = {
  R0: 'text-slate-300',
  R1: 'text-sky-300',
  R2: 'text-amber-300',
  R3: 'text-orange-300',
  R4: 'text-rose-300',
  R5: 'text-red-300',
}

function riskAccent(level) {
  return RISK_ACCENT[level] || RISK_ACCENT.R0
}

function formatDateTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const date = d.toLocaleDateString('id-ID', {
    timeZone: 'Asia/Jakarta',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
  const time = d.toLocaleTimeString('id-ID', {
    timeZone: 'Asia/Jakarta',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
  return `${date} · ${time} WIB`
}

function outletLabel(issue) {
  return issue?.source_label || null
}

function influenceScore(issue) {
  const assessment =
    issue?.risk_assessment && typeof issue.risk_assessment === 'object'
      ? issue.risk_assessment
      : {}

  const ratio = Number(assessment.sentiment_negative_ratio)
  if (Number.isFinite(ratio) && ratio > 0) {
    return Math.min(10, Math.max(1, Math.round(ratio * 10)))
  }

  for (const key of ['sentiment_score', 'score', 'severity_score', 'influence_score']) {
    const raw = Number(assessment[key])
    if (!Number.isFinite(raw)) continue
    if (raw <= 10) return Math.min(10, Math.max(1, Math.round(Math.abs(raw))))
    return Math.min(10, Math.max(1, Math.round(Math.abs(raw) / 10)))
  }

  const riskMap = { R0: 1, R1: 3, R2: 5, R3: 7, R4: 8, R5: 10 }
  return riskMap[issue?.risk_level] || 3
}

function scoreBarClass(score) {
  if (score >= 8) return 'bg-rose-500'
  if (score >= 6) return 'bg-orange-500'
  if (score >= 4) return 'bg-amber-400'
  return 'bg-sky-500'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {
      page: page.value,
      per_page: 10,
      sync: '1',
      days: periodStore.days,
      sort_by: filters.value.sort_by,
      sort_dir: filters.value.sort_dir,
    }
    for (const [k, v] of Object.entries(filters.value)) {
      if (k === 'sort_by' || k === 'sort_dir') continue
      if (v) params[k] = v
    }
    const issuesRes = await api.get('/issues', { params })
    issues.value = issuesRes.data.data || []
    meta.value = issuesRes.data.meta || null
    syncInfo.value = issuesRes.data.sipantau_sync || null
    const sum = issuesRes.data.summary || {}
    summary.value = {
      open: sum.open || 0,
      elevated: sum.elevated || 0,
      by_risk: {
        R0: 0,
        R1: 0,
        R2: 0,
        R3: 0,
        R4: 0,
        R5: 0,
        ...(sum.by_risk || {}),
      },
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat data Crisis Room'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  load()
}

function resetFilters() {
  filters.value = {
    q: '',
    status: '',
    risk_level: '',
    sort_by: 'created_at',
    sort_dir: 'desc',
  }
  page.value = 1
  load()
}

function filterByRisk(level) {
  filters.value.risk_level = filters.value.risk_level === level ? '' : level
  page.value = 1
  load()
}

function onSortChange() {
  page.value = 1
  load()
}

function toggleSortDir() {
  filters.value.sort_dir = filters.value.sort_dir === 'asc' ? 'desc' : 'asc'
  page.value = 1
  load()
}

function onPage(p) {
  if (!meta.value) return
  if (p < 1 || p > (meta.value.pages || 1)) return
  page.value = p
  load()
}

async function createIssue() {
  creating.value = true
  createError.value = ''
  try {
    await api.post('/issues', form.value)
    showCreate.value = false
    form.value = { title: '', summary: '', why_now: '', risk_level: 'R2' }
    page.value = 1
    await load()
  } catch (err) {
    createError.value = err.response?.data?.error || 'Gagal membuat isu'
  } finally {
    creating.value = false
  }
}

function visitSource(event, issue) {
  event.preventDefault()
  event.stopPropagation()
  const url = issue?.source_url
  if (!url) return
  window.open(url, '_blank', 'noopener,noreferrer')
}

async function addToPdf(event, issue) {
  event.preventDefault()
  event.stopPropagation()
  if (!issue?.id || pdfBusyId.value) return
  pdfBusyId.value = issue.id
  actionError.value = ''
  try {
    const res = await api.get('/reports/export/crisis', {
      params: { format: 'pdf', issue_id: issue.id },
      responseType: 'blob',
    })
    const disposition = res.headers['content-disposition'] || ''
    const match = disposition.match(/filename="?([^"]+)"?/)
    const filename = match?.[1] || `laporan-crisis-${issue.id}.pdf`
    const blobUrl = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = filename
    a.click()
    URL.revokeObjectURL(blobUrl)
  } catch (err) {
    let msg = 'Gagal membuat PDF'
    try {
      const text = await err.response?.data?.text?.()
      if (text) msg = JSON.parse(text).error || msg
    } catch {
      /* ignore */
    }
    actionError.value = msg
  } finally {
    pdfBusyId.value = null
  }
}

async function deleteIssue(event, issue) {
  event.preventDefault()
  event.stopPropagation()
  if (!canDelete.value || !issue?.id || deletingId.value) return
  const ok = window.confirm(`Hapus isu “${issue.title}”? Tindakan ini tidak bisa dibatalkan.`)
  if (!ok) return
  deletingId.value = issue.id
  actionError.value = ''
  try {
    await api.delete(`/issues/${issue.id}`)
    await load()
  } catch (err) {
    actionError.value = err.response?.data?.error || 'Gagal menghapus isu'
  } finally {
    deletingId.value = null
  }
}

onMounted(load)

watch(
  () => projectStore.selectedId,
  () => {
    page.value = 1
    load()
  },
)

watch(
  () => periodStore.period,
  () => {
    page.value = 1
    load()
  },
)
</script>

<template>
  <div class="space-y-6">
    <!-- Hero -->
    <section
      class="rounded-xl border border-[#30363d] bg-[#161b22] px-4 py-3.5 sm:px-5"
    >
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="min-w-0 flex flex-wrap items-center gap-2.5">
          <span
            class="inline-flex items-center gap-1.5 rounded-md border border-rose-500/30 bg-rose-500/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-rose-300"
          >
            <span class="relative flex h-1.5 w-1.5">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-60" />
              <span class="relative inline-flex h-1.5 w-1.5 rounded-full bg-rose-400" />
            </span>
            Live
          </span>
          <div class="min-w-0">
            <h1 class="text-lg font-bold tracking-tight text-white sm:text-xl">Crisis Room</h1>
            <p class="text-[11px] text-[#6e7681]">
              Ruang kendali isu sensitif — pantauan otomatis &amp; input manual
            </p>
          </div>
          <span
            v-if="syncInfo && !syncInfo.error && !syncInfo.skipped"
            class="hidden text-[11px] text-[#6e7681] sm:inline"
          >
            Sync {{ syncInfo.candidates || 0 }} · {{ syncInfo.pushed || 0 }} masuk
          </span>
        </div>

        <button
          v-if="canCreate"
          type="button"
          class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-500/40 bg-emerald-500/15 px-3 py-1.5 text-xs font-semibold text-emerald-300 transition hover:bg-emerald-500/25"
          @click="showCreate = !showCreate"
        >
          <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path v-if="!showCreate" stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
          {{ showCreate ? 'Tutup' : 'Input manual' }}
        </button>
      </div>

      <div class="mt-3 grid grid-cols-3 gap-2 sm:grid-cols-3">
        <div class="rounded-lg border border-[#30363d] bg-[#0d1117]/60 px-3 py-2">
          <p class="text-[9px] font-semibold uppercase tracking-wider text-[#6e7681]">Total</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-white">{{ totalIssues }}</p>
        </div>
        <div class="rounded-lg border border-[#30363d] bg-[#0d1117]/60 px-3 py-2">
          <p class="text-[9px] font-semibold uppercase tracking-wider text-[#6e7681]">Open</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-emerald-400">{{ summary.open }}</p>
        </div>
        <div class="rounded-lg border border-[#30363d] bg-[#0d1117]/60 px-3 py-2">
          <p class="text-[9px] font-semibold uppercase tracking-wider text-[#6e7681]">Elevated+</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-rose-400">{{ summary.elevated }}</p>
        </div>
      </div>

      <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        <button
          v-for="card in riskCards"
          :key="card.level"
          type="button"
          class="rounded-lg border px-2.5 py-2 text-left transition"
          :class="
            filters.risk_level === card.level
              ? 'border-emerald-500/40 bg-emerald-500/10'
              : 'border-[#30363d] bg-[#0d1117]/60 hover:border-[#484f58]'
          "
          :title="card.title"
          @click="filterByRisk(card.level)"
        >
          <div class="flex items-baseline justify-between gap-1">
            <p class="text-[10px] font-bold tracking-wide" :class="RISK_CARD_CLASS[card.level] || 'text-[#c9d1d9]'">
              {{ card.label }}
            </p>
            <p class="text-base font-bold tabular-nums text-white sm:text-lg">{{ card.count }}</p>
          </div>
          <p class="mt-0.5 text-[10px] font-semibold text-[#c9d1d9]">{{ card.short }}</p>
          <p class="mt-0.5 line-clamp-2 text-[9px] leading-snug text-[#6e7681]">{{ card.description }}</p>
        </button>
      </div>
    </section>

    <!-- Filters -->
    <form
      class="overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
      @submit.prevent="applyFilters"
    >
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#30363d]/80 px-4 py-3 sm:px-5">
        <div class="flex items-center gap-2">
          <span
            class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#30363d] bg-[#0d1117] text-[#8b949e]"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 4.5h18M6 9.75h12M9 15h6M11 20.25h2" />
            </svg>
          </span>
          <div>
            <p class="text-sm font-semibold text-white">Filter isu</p>
            <p class="text-[11px] text-[#6e7681]">
              {{ hasActiveFilters ? `${activeFilterCount} filter aktif` : 'Saring antrian Crisis Room' }}
            </p>
          </div>
        </div>
        <button
          v-if="hasActiveFilters"
          type="button"
          class="rounded-lg px-2.5 py-1.5 text-[11px] font-semibold text-[#8b949e] transition hover:bg-[#21262d] hover:text-white"
          @click="resetFilters"
        >
          Hapus semua
        </button>
      </div>

      <div class="space-y-3 p-4 sm:p-5">
        <div class="relative">
          <svg
            class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#6e7681]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="1.75"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-4.35-4.35M11 18a7 7 0 1 1 0-14 7 7 0 0 1 0 14Z" />
          </svg>
          <input
            v-model="filters.q"
            type="search"
            placeholder="Cari judul, ringkasan, atau alert ID…"
            class="w-full rounded-xl border border-[#30363d] bg-[#0d1117] py-2.5 pl-10 pr-3 text-sm text-[#e6edf3] placeholder:text-[#6e7681] outline-none transition focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30"
          />
        </div>

        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 sm:items-end">
          <label class="block min-w-0">
            <span class="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Status</span>
            <div class="relative">
              <select v-model="filters.status" :class="filterControlClass">
                <option value="">Semua status</option>
                <option
                  v-for="s in ISSUE_STATUSES"
                  :key="s"
                  :value="s"
                  :title="issueStatusOptionLabel(s)"
                >
                  {{ issueStatusMeta(s).short }}
                </option>
              </select>
              <svg class="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#6e7681]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
              </svg>
            </div>
          </label>

          <label class="block min-w-0">
            <span class="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Risk</span>
            <div class="relative">
              <select v-model="filters.risk_level" :class="filterControlClass" :title="RISK_LEVELS.map(riskTitle).join(' · ')">
                <option value="">Semua level</option>
                <option v-for="r in RISK_LEVELS" :key="r" :value="r" :title="riskTitle(r)">
                  {{ riskOptionLabel(r) }}
                </option>
              </select>
              <svg class="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#6e7681]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
              </svg>
            </div>
          </label>

          <label class="block min-w-0">
            <span class="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Urutkan</span>
            <div class="flex gap-2">
              <div class="relative min-w-0 flex-1">
                <select v-model="filters.sort_by" :class="filterControlClass" @change="onSortChange">
                  <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
                <svg class="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#6e7681]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
                </svg>
              </div>
              <button
                type="button"
                class="shrink-0 rounded-xl border border-[#30363d] px-3 py-2.5 text-xs font-semibold text-[#c9d1d9] transition hover:border-[#484f58] hover:bg-[#21262d]"
                :title="filters.sort_dir === 'asc' ? 'Naik' : 'Turun'"
                @click="toggleSortDir"
              >
                {{ filters.sort_dir === 'asc' ? '↑' : '↓' }}
              </button>
            </div>
          </label>

          <div class="flex flex-wrap gap-2">
            <button
              type="submit"
              class="inline-flex items-center gap-1.5 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-emerald-400"
            >
              Terapkan
            </button>
            <button
              type="button"
              class="rounded-xl border border-[#30363d] px-4 py-2.5 text-sm font-medium text-[#c9d1d9] transition hover:border-[#484f58] hover:bg-[#21262d] hover:text-white"
              @click="resetFilters"
            >
              Reset
            </button>
          </div>
        </div>
      </div>
    </form>

    <!-- Create -->
    <form
      v-if="showCreate"
      class="rounded-2xl border border-emerald-500/25 bg-[#161b22] p-5 shadow-[0_0_40px_-20px_rgba(16,185,129,0.35)]"
      @submit.prevent="createIssue"
    >
      <h2 class="text-base font-semibold text-white">Input isu manual</h2>
      <p class="mt-1 text-xs text-[#8b949e]">Isu akan berstatus open dan muncul di antrian Crisis Room.</p>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="text-[11px] font-medium text-[#8b949e]">Judul</label>
          <input v-model="form.title" required :class="inputClass" />
        </div>
        <div class="md:col-span-2">
          <label class="text-[11px] font-medium text-[#8b949e]">Ringkasan</label>
          <textarea v-model="form.summary" rows="2" :class="inputClass" />
        </div>
        <div>
          <label class="text-[11px] font-medium text-[#8b949e]">Why now</label>
          <input v-model="form.why_now" :class="inputClass" />
        </div>
        <div>
          <label class="text-[11px] font-medium text-[#8b949e]">Risk level</label>
          <select v-model="form.risk_level" :class="inputClass">
            <option v-for="r in RISK_LEVELS" :key="r" :value="r" :title="riskTitle(r)">
              {{ riskOptionLabel(r) }}
            </option>
          </select>
          <p class="mt-1 text-[11px] text-[#6e7681]">{{ riskTitle(form.risk_level) }}</p>
        </div>
      </div>
      <p v-if="createError" class="mt-3 text-sm text-rose-400">{{ createError }}</p>
      <button
        type="submit"
        class="mt-4 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black transition hover:bg-emerald-400 disabled:opacity-60"
        :disabled="creating"
      >
        {{ creating ? 'Menyimpan…' : 'Simpan isu' }}
      </button>
    </form>

    <!-- List -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="n in 4"
        :key="n"
        class="h-36 animate-pulse rounded-2xl border border-[#30363d] bg-[#161b22]"
      />
    </div>

    <div
      v-else-if="error"
      class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300"
    >
      {{ error }}
    </div>

    <div
      v-if="actionError"
      class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300"
    >
      {{ actionError }}
    </div>

    <div
      v-else-if="!issues.length"
      class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22]/60 px-6 py-16 text-center"
    >
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-[#30363d] bg-[#0d1117] text-[#8b949e]"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
          />
        </svg>
      </div>
      <p class="mt-4 text-lg font-semibold text-white">Belum ada isu di antrian</p>
      <p class="mx-auto mt-2 max-w-md text-sm text-[#8b949e]">
        Mention negatif dari pantauan akan masuk otomatis, atau buat isu manual.
      </p>
    </div>

    <div v-else class="space-y-3">
      <RouterLink
        v-for="issue in issues"
        :key="issue.id"
        :to="`/issues/${issue.id}`"
        class="group relative block overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] transition duration-200 hover:-translate-y-0.5 hover:border-emerald-500/35 hover:shadow-[0_12px_40px_-24px_rgba(16,185,129,0.45)]"
      >
        <div
          class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent"
          :class="riskAccent(issue.risk_level)"
          aria-hidden="true"
        />
        <div class="flex flex-wrap items-start justify-between gap-3 px-5 py-4 pl-6">
          <div class="min-w-0 flex-1">
            <div class="flex items-start justify-between gap-3">
              <h2 class="text-base font-semibold leading-snug text-white transition group-hover:text-emerald-300 sm:text-lg">
                {{ issue.title }}
              </h2>
              <IssueStatusBadge :status="issue.status" tone="outline" class="shrink-0" />
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2">
              <RiskBadge :level="issue.risk_level" show-label tone="outline" />
              <span
                v-if="outletLabel(issue)"
                class="inline-flex items-center rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]"
              >
                {{ outletLabel(issue) }}
              </span>
              <span class="inline-flex items-center gap-1.5 text-[11px] text-[#8b949e]">
                <span>Influence score: {{ influenceScore(issue) }}/10</span>
                <span class="inline-flex h-1.5 w-14 overflow-hidden rounded-full bg-[#30363d]" aria-hidden="true">
                  <span
                    class="h-full rounded-full transition"
                    :class="scoreBarClass(influenceScore(issue))"
                    :style="{ width: `${influenceScore(issue) * 10}%` }"
                  />
                </span>
              </span>
              <span
                v-if="issue.created_at"
                class="inline-flex items-center gap-1 text-[11px] text-[#6e7681]"
                :title="formatDateTime(issue.created_at)"
              >
                <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l3.5 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
                {{ formatDateTime(issue.created_at) }}
              </span>
            </div>
            <p class="mt-1.5 line-clamp-2 text-sm leading-relaxed text-[#8b949e]">
              {{ issue.summary || issue.why_now || 'Tidak ada ringkasan' }}
            </p>
          </div>
        </div>

        <div
          class="flex flex-wrap items-center justify-between gap-2 border-t border-[#30363d]/80 px-5 py-2.5 pl-6"
        >
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px] font-medium">
            <button
              type="button"
              class="inline-flex items-center gap-1.5 text-sky-400 transition hover:text-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="!issue.source_url"
              :title="issue.source_url ? 'Buka berita di tab baru' : 'URL berita tidak tersedia'"
              @click="visitSource($event, issue)"
            >
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Visit
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-1.5 text-sky-400 transition hover:text-emerald-400 disabled:opacity-50"
              :disabled="pdfBusyId === issue.id"
              @click="addToPdf($event, issue)"
            >
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m.75 12 3 3m0 0 3-3m-3 3v-6m-7.5 6h16.5"
                />
              </svg>
              {{ pdfBusyId === issue.id ? 'PDF…' : 'Add to PDF' }}
            </button>
            <button
              v-if="canDelete"
              type="button"
              class="inline-flex items-center gap-1.5 text-rose-400/90 transition hover:text-rose-300 disabled:opacity-50"
              :disabled="deletingId === issue.id"
              @click="deleteIssue($event, issue)"
            >
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                />
              </svg>
              {{ deletingId === issue.id ? 'Menghapus…' : 'Delete' }}
            </button>
          </div>
          <span
            class="inline-flex items-center gap-1 text-[11px] font-medium text-[#6e7681] transition group-hover:text-emerald-400"
          >
            Detail
            <svg class="h-3.5 w-3.5 transition group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </span>
        </div>
      </RouterLink>
    </div>

    <div
      v-if="meta && meta.total > 0"
      class="flex flex-wrap items-center justify-between gap-3 border-t border-[#30363d] pt-4 text-sm"
    >
      <p class="text-[#8b949e]">
        Menampilkan
        <span class="font-medium text-[#e6edf3]">
          {{ (meta.page - 1) * meta.per_page + 1 }}–{{ Math.min(meta.page * meta.per_page, meta.total) }}
        </span>
        dari
        <span class="font-medium text-[#e6edf3]">{{ meta.total }}</span>
      </p>
      <div class="flex items-center gap-1.5">
        <button
          type="button"
          class="rounded-lg border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-[#c9d1d9] transition hover:border-[#484f58] hover:text-white disabled:opacity-40"
          :disabled="!meta.has_prev"
          @click="onPage(meta.page - 1)"
        >
          ‹ Prev
        </button>
        <span class="min-w-16 px-2 text-center tabular-nums text-[#8b949e]">
          {{ meta.page }} / {{ meta.pages || 1 }}
        </span>
        <button
          type="button"
          class="rounded-lg border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-[#c9d1d9] transition hover:border-[#484f58] hover:text-white disabled:opacity-40"
          :disabled="!meta.has_next"
          @click="onPage(meta.page + 1)"
        >
          Next ›
        </button>
      </div>
    </div>
  </div>
</template>
