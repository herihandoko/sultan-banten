<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import PaginationBar from '../components/PaginationBar.vue'
import RiskBadge from '../components/RiskBadge.vue'
import IssueStatusBadge from '../components/IssueStatusBadge.vue'
import { RISK_LEVELS, riskOptionLabel, riskTitle } from '../config/risk'
import { ISSUE_STATUSES, issueStatusOptionLabel } from '../config/issueStatus'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const issues = ref([])
const contents = ref([])
const meta = ref({})
const issuesPage = ref(Number(route.query.issues_page) || 1)
const contentsPage = ref(Number(route.query.contents_page) || 1)
const expandedId = ref(null)

const filters = ref({
  q: route.query.q || '',
  type: route.query.type || 'all',
  status: route.query.status || '',
  risk_level: route.query.risk_level || '',
  source: route.query.source || '',
  date_from: route.query.date_from || '',
  date_to: route.query.date_to || '',
})

async function search() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    for (const [k, v] of Object.entries(filters.value)) {
      if (v) params[k] = v
    }
    params.issues_page = issuesPage.value
    params.contents_page = contentsPage.value
    params.per_page = 10
    const { data } = await api.get('/archive', { params })
    issues.value = data.data.issues || []
    contents.value = data.data.contents || []
    meta.value = data.meta || {}
    router.replace({ query: { ...params } })
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat arsip'
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.value = {
    q: '',
    type: 'all',
    status: '',
    risk_level: '',
    source: '',
    date_from: '',
    date_to: '',
  }
  issuesPage.value = 1
  contentsPage.value = 1
  search()
}

function onIssuesPage(p) {
  issuesPage.value = p
  search()
}

function onContentsPage(p) {
  contentsPage.value = p
  search()
}

function toggleTimeline(id) {
  expandedId.value = expandedId.value === id ? null : id
}

const RISK_ACCENT = {
  R0: 'from-slate-400/80',
  R1: 'from-sky-400/80',
  R2: 'from-amber-400/80',
  R3: 'from-orange-400/80',
  R4: 'from-rose-400/80',
  R5: 'from-red-500/80',
}

const CONTENT_STATUS = {
  draft: { label: 'Draft', chip: 'border-slate-500/40 bg-slate-500/10 text-slate-300', accent: 'from-slate-400/80' },
  in_review: { label: 'Review', chip: 'border-amber-500/40 bg-amber-500/10 text-amber-300', accent: 'from-amber-400/80' },
  approved: { label: 'Disetujui', chip: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300', accent: 'from-emerald-500/80' },
  rejected: { label: 'Ditolak', chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300', accent: 'from-rose-500/80' },
  published: { label: 'Terbit', chip: 'border-sky-500/40 bg-sky-500/10 text-sky-300', accent: 'from-sky-500/80' },
}

const CONTENT_TYPE = {
  text_release: { label: 'Rilis Teks', accent: 'from-sky-500/80' },
  infographic: { label: 'Infografis', accent: 'from-amber-400/80' },
  video: { label: 'Video', accent: 'from-violet-500/80' },
}

const SOURCE_LABEL = {
  mata_bathin: 'Mata Bathin',
  sipantau: 'SIPANTAU',
  manual: 'Manual',
}

function riskAccent(level) {
  return RISK_ACCENT[level] || 'from-slate-400/80'
}

function contentStatus(item) {
  return CONTENT_STATUS[item.status] || { label: item.status, chip: 'border-[#30363d] text-[#c9d1d9]', accent: 'from-slate-400/80' }
}

function contentType(item) {
  return CONTENT_TYPE[item.content_type] || { label: item.content_type, accent: 'from-slate-400/80' }
}

function sourceLabel(source) {
  return SOURCE_LABEL[source] || source || '—'
}

function formatDateTime(iso) {
  if (!iso) return ''
  const normalized = /[zZ]|[+-]\d{2}:\d{2}$/.test(iso) ? iso : `${iso}Z`
  const d = new Date(normalized)
  if (Number.isNaN(d.getTime())) return iso
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

function excerpt(text) {
  const clean = (text || '').replace(/\s+/g, ' ').trim()
  if (!clean) return 'Belum ada ringkasan.'
  return clean.length > 180 ? `${clean.slice(0, 177)}…` : clean
}

onMounted(search)

watch(
  () => filters.value.type,
  () => {
    issuesPage.value = 1
    contentsPage.value = 1
    search()
  },
)
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="font-display text-3xl text-banten-navy">Arsip Isu & Konten</h1>
      <p class="mt-1 text-sm text-banten-navy/65">
        F.05 — Histori penanganan, evidence, timeline respons, dan konten terkait
      </p>
    </div>

    <form
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-4"
      @submit.prevent="issuesPage = 1; contentsPage = 1; search()"
    >
      <div class="grid gap-3 md:grid-cols-4">
        <div class="md:col-span-2">
          <label class="text-xs font-medium text-banten-navy/70">Kata kunci</label>
          <input
            v-model="filters.q"
            type="search"
            placeholder="Judul, ringkasan, alert ID..."
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Tipe</label>
          <select v-model="filters.type" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="all">Isu + Konten</option>
            <option value="issues">Isu saja</option>
            <option value="content">Konten saja</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Status isu</label>
          <select v-model="filters.status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option v-for="s in ISSUE_STATUSES" :key="s" :value="s" :title="issueStatusOptionLabel(s)">
              {{ issueStatusOptionLabel(s) }}
            </option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70" :title="RISK_LEVELS.map(riskTitle).join(' · ')">
            Risk level
          </label>
          <select v-model="filters.risk_level" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option v-for="r in RISK_LEVELS" :key="r" :value="r" :title="riskTitle(r)">
              {{ riskOptionLabel(r) }}
            </option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Sumber</label>
          <select v-model="filters.source" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option value="mata_bathin">Mata Bathin</option>
            <option value="manual">Manual</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Dari tanggal</label>
          <input v-model="filters.date_from" type="date" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Sampai tanggal</label>
          <input v-model="filters.date_to" type="date" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
        </div>
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button type="submit" class="rounded-md bg-banten-navy px-4 py-2 text-sm text-white">
          Cari Arsip
        </button>
        <button type="button" class="rounded-md border border-banten-navy/20 px-4 py-2 text-sm text-banten-navy" @click="resetFilters">
          Reset
        </button>
      </div>
    </form>

    <div v-if="loading" class="text-sm text-banten-navy/60">Mencari...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <template v-else>
      <p class="mb-4 text-xs text-banten-navy/55">
        Hasil: {{ meta.issues_count || 0 }} isu · {{ meta.contents_count || 0 }} konten
      </p>

      <section v-if="filters.type !== 'content'" class="mb-8">
        <h2 class="mb-3 font-display text-xl text-banten-navy">Isu</h2>
        <div
          v-if="!issues.length"
          class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22]/60 px-6 py-12 text-center text-sm text-[#8b949e]"
        >
          Tidak ada isu yang cocok.
        </div>
        <div v-else class="space-y-3">
          <article
            v-for="issue in issues"
            :key="issue.id"
            class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
          >
            <div
              class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent"
              :class="riskAccent(issue.risk_level)"
              aria-hidden="true"
            />
            <div class="px-5 py-4 pl-6">
              <div class="flex items-start justify-between gap-3">
                <h3 class="text-base font-semibold leading-snug text-white sm:text-lg">
                  <RouterLink :to="`/issues/${issue.id}`" class="transition hover:text-emerald-300">
                    {{ issue.title }}
                  </RouterLink>
                </h3>
                <IssueStatusBadge :status="issue.status" tone="outline" class="shrink-0" />
              </div>
              <div class="mt-2 flex flex-wrap items-center gap-2">
                <RiskBadge :level="issue.risk_level" show-label tone="outline" />
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
                  {{ issue.source_label || sourceLabel(issue.source) }}
                </span>
                <span v-if="issue.created_at" class="text-[11px] text-[#6e7681]">
                  {{ formatDateTime(issue.created_at) }}
                </span>
              </div>
              <p class="mt-2 line-clamp-2 text-sm leading-relaxed text-[#8b949e]">
                {{ excerpt(issue.summary || issue.why_now) }}
              </p>
              <div class="mt-3 flex flex-wrap gap-2">
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
                  {{ issue.archive.evidence_count }} evidence
                </span>
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
                  Validasi {{ issue.archive.validated_count }}/{{ issue.archive.validation_count }}
                </span>
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
                  Konten {{ issue.archive.content_approved }}/{{ issue.archive.content_count }}
                </span>
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-sky-300">
                  {{ issue.archive.blast_count }} blast
                </span>
              </div>
            </div>
            <div class="flex items-center justify-between gap-3 border-t border-[#30363d]/80 px-5 py-2.5 pl-6">
              <RouterLink :to="`/issues/${issue.id}`" class="text-[11px] font-medium text-[#6e7681] hover:text-emerald-400">
                Buka isu
              </RouterLink>
              <button
                type="button"
                class="text-[11px] font-semibold text-emerald-300 hover:text-emerald-200"
                @click="toggleTimeline(issue.id)"
              >
                {{ expandedId === issue.id ? 'Tutup timeline' : 'Lihat timeline' }}
              </button>
            </div>
            <ol
              v-if="expandedId === issue.id"
              class="space-y-2 border-t border-[#30363d]/80 px-5 py-3 pl-6"
            >
              <li
                v-for="(ev, idx) in issue.archive.timeline"
                :key="idx"
                class="flex gap-3 text-xs"
              >
                <span class="w-44 shrink-0 text-[#6e7681]">{{ formatDateTime(ev.at) }}</span>
                <span class="text-[#c9d1d9]">{{ ev.label }}</span>
              </li>
              <li v-if="!issue.archive.timeline?.length" class="text-xs text-[#8b949e]">
                Belum ada jejak penanganan.
              </li>
            </ol>
          </article>
        </div>
        <PaginationBar :meta="meta.issues" @update:page="onIssuesPage" />
      </section>

      <section v-if="filters.type !== 'issues'">
        <h2 class="mb-3 font-display text-xl text-banten-navy">Konten</h2>
        <div
          v-if="!contents.length"
          class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22]/60 px-6 py-12 text-center text-sm text-[#8b949e]"
        >
          Tidak ada konten yang cocok.
        </div>
        <div v-else class="space-y-3">
          <RouterLink
            v-for="c in contents"
            :key="c.id"
            :to="`/konten/${c.id}`"
            class="group relative block overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] transition duration-200 hover:-translate-y-0.5 hover:border-emerald-500/35"
          >
            <div
              class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent"
              :class="contentType(c).accent"
              aria-hidden="true"
            />
            <div class="px-5 py-4 pl-6">
              <div class="flex items-start justify-between gap-3">
                <h3 class="text-base font-semibold leading-snug text-white transition group-hover:text-emerald-300">
                  {{ c.title }}
                </h3>
                <span
                  class="shrink-0 rounded-md border px-2 py-0.5 text-[11px] font-semibold"
                  :class="contentStatus(c).chip"
                >
                  {{ contentStatus(c).label }}
                </span>
              </div>
              <div class="mt-2 flex flex-wrap items-center gap-2">
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
                  {{ contentType(c).label }}
                </span>
                <RiskBadge v-if="c.issue_risk_level" :level="c.issue_risk_level" show-label tone="outline" />
                <span v-if="c.updated_at || c.created_at" class="text-[11px] text-[#6e7681]">
                  {{ formatDateTime(c.updated_at || c.created_at) }}
                </span>
              </div>
              <p class="mt-2 line-clamp-2 text-sm leading-relaxed text-[#8b949e]">
                {{ excerpt(c.body) }}
              </p>
              <p class="mt-1 truncate text-xs text-[#6e7681]">
                Isu: {{ c.issue_title || `#${c.issue_id}` }}
              </p>
            </div>
            <div class="flex items-center justify-end border-t border-[#30363d]/80 px-5 py-2.5 pl-6">
              <span class="text-[11px] font-medium text-[#6e7681] transition group-hover:text-emerald-400">
                Buka naskah
              </span>
            </div>
          </RouterLink>
        </div>
        <PaginationBar :meta="meta.contents" @update:page="onContentsPage" />
      </section>
    </template>
  </div>
</template>
