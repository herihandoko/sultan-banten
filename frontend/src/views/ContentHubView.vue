<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import RiskBadge from '../components/RiskBadge.vue'
import { riskOptionLabel } from '../config/risk'
import { draftFromIssue } from '../config/contentDraft'
import ContentDraftFields from '../components/ContentDraftFields.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const items = ref([])
const meta = ref(null)
const page = ref(1)
const issues = ref([])
const loading = ref(true)
const error = ref('')
const filters = ref({
  q: '',
  status: route.query.status || '',
  content_type: '',
})
const showCreate = ref(Boolean(route.query.issue_id))
const creating = ref(false)
const formError = ref('')
const form = ref({
  issue_id: route.query.issue_id ? String(route.query.issue_id) : '',
  title: '',
  content_type: 'text_release',
  body: '',
  media_url: '',
})

const STATUS_META = {
  draft: { label: 'Draft', hint: 'Masih disusun', chip: 'border-slate-500/40 bg-slate-500/10 text-slate-300', count: 'text-slate-300' },
  in_review: { label: 'Review', hint: 'Menunggu pimpinan', chip: 'border-amber-500/40 bg-amber-500/10 text-amber-300', count: 'text-amber-300' },
  approved: { label: 'Disetujui', hint: 'Siap disebar', chip: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300', count: 'text-emerald-300' },
  rejected: { label: 'Ditolak', hint: 'Perlu revisi', chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300', count: 'text-rose-300' },
  published: { label: 'Terbit', hint: 'Sudah disebar', chip: 'border-sky-500/40 bg-sky-500/10 text-sky-300', count: 'text-sky-300' },
}

const TYPE_META = {
  text_release: { label: 'Rilis Teks', hint: 'Naskah media', accent: 'from-sky-500/80' },
  infographic: { label: 'Infografis', hint: 'Kartu fakta', accent: 'from-amber-400/80' },
  video: { label: 'Video', hint: 'Naskah bicara', accent: 'from-violet-500/80' },
}

const summary = ref({
  total: 0,
  by_status: { draft: 0, in_review: 0, approved: 0, rejected: 0, published: 0 },
  by_type: { text_release: 0, infographic: 0, video: 0 },
})

const filterControlClass =
  'w-full appearance-none rounded-xl border border-[#30363d] bg-[#0d1117] py-2.5 pl-3 pr-8 text-sm text-[#e6edf3] outline-none transition hover:border-[#484f58] focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'
const autofill = ref({ title: '', body: '' })

const canEdit = computed(() => {
  const code = auth.user?.role?.code
  return code === 'super_admin' || code === 'editor'
})

const selectedIssue = computed(() =>
  issues.value.find((i) => String(i.id) === String(form.value.issue_id)),
)

const issueOptions = computed(() =>
  issues.value.map((issue) => ({
    value: issue.id,
    label: `${riskOptionLabel(issue.risk_level)} · ${issue.title} (${issue.status})`,
  })),
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, per_page: 10 }
    for (const [k, v] of Object.entries(filters.value)) {
      if (v) params[k] = v
    }
    const reqs = [api.get('/content', { params })]
    if (canEdit.value) reqs.push(api.get('/content/issues-ready'))
    const [contentRes, issuesRes] = await Promise.all(reqs)
    items.value = contentRes.data.data || []
    meta.value = contentRes.data.meta || null
    summary.value = {
      total: contentRes.data.summary?.total || 0,
      by_status: { ...summary.value.by_status, ...(contentRes.data.summary?.by_status || {}) },
      by_type: { ...summary.value.by_type, ...(contentRes.data.summary?.by_type || {}) },
    }
    if (issuesRes) issues.value = issuesRes.data.data || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat Hub Konten'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  load()
}

function resetFilters() {
  filters.value = { q: '', status: '', content_type: '' }
  page.value = 1
  load()
}

function onPage(p) {
  page.value = p
  load()
}

function filterByStatus(status) {
  filters.value.status = filters.value.status === status ? '' : status
  applyFilters()
}

function filterByType(type) {
  filters.value.content_type = filters.value.content_type === type ? '' : type
  applyFilters()
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

function excerpt(body) {
  const text = (body || '').replace(/\s+/g, ' ').trim()
  if (!text) return 'Belum ada naskah.'
  return text.length > 180 ? `${text.slice(0, 177)}…` : text
}

function statusOf(item) {
  return STATUS_META[item.status] || { label: item.status, chip: 'border-[#30363d] text-[#c9d1d9]' }
}

function typeOf(item) {
  return TYPE_META[item.content_type] || { label: item.content_type, accent: 'from-slate-500/80' }
}

watch(
  [selectedIssue, () => form.value.content_type],
  ([issue, type]) => {
    if (!issue) return
    const draft = draftFromIssue(issue, type)
    const titleUntouched = !form.value.title || form.value.title === autofill.value.title
    const bodyUntouched = !form.value.body || form.value.body === autofill.value.body
    if (titleUntouched) form.value.title = draft.title
    if (bodyUntouched) form.value.body = draft.body
    if (type === 'text_release') form.value.media_url = ''
    autofill.value = draft
  },
)

async function createContent() {
  creating.value = true
  formError.value = ''
  try {
    const payload = {
      ...form.value,
      issue_id: Number(form.value.issue_id),
    }
    const { data } = await api.post('/content', payload)
    showCreate.value = false
    form.value = {
      issue_id: '',
      title: '',
      content_type: 'text_release',
      body: '',
      media_url: '',
    }
    autofill.value = { title: '', body: '' }
    await load()
    router.push(`/konten/${data.data.id}`)
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal membuat konten'
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-400/80">F.04 · Produksi</p>
        <h1 class="mt-1 font-display text-3xl text-white">Hub Konten Klarifikasi</h1>
        <p class="mt-1 text-sm text-[#8b949e]">
          Rilis, infografis, dan video — dari draft sampai disetujui untuk disebar.
        </p>
      </div>
      <button
        v-if="canEdit"
        type="button"
        class="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-emerald-400"
        @click="showCreate = !showCreate"
      >
        {{ showCreate ? 'Tutup' : '+ Buat Konten' }}
      </button>
    </div>

    <section class="mb-6 rounded-2xl border border-[#30363d] bg-[#161b22] p-4 sm:p-5">
      <div class="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        <button
          type="button"
          class="rounded-lg border px-3 py-2 text-left transition"
          :class="!filters.status ? 'border-emerald-500/40 bg-emerald-500/10' : 'border-[#30363d] bg-[#0d1117]/60 hover:border-[#484f58]'"
          @click="filters.status = ''; applyFilters()"
        >
          <p class="text-[10px] font-semibold uppercase tracking-wider text-[#6e7681]">Semua</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-white">{{ summary.total }}</p>
        </button>
        <button
          v-for="(meta, key) in STATUS_META"
          :key="key"
          type="button"
          class="rounded-lg border px-3 py-2 text-left transition"
          :class="filters.status === key ? 'border-emerald-500/40 bg-emerald-500/10' : 'border-[#30363d] bg-[#0d1117]/60 hover:border-[#484f58]'"
          @click="filterByStatus(key)"
        >
          <p class="text-[10px] font-semibold uppercase tracking-wider" :class="meta.count">{{ meta.label }}</p>
          <p class="mt-0.5 text-lg font-bold tabular-nums text-white">{{ summary.by_status[key] || 0 }}</p>
          <p class="text-[10px] text-[#6e7681]">{{ meta.hint }}</p>
        </button>
      </div>
      <div class="mt-3 grid gap-2 sm:grid-cols-3">
        <button
          v-for="(meta, key) in TYPE_META"
          :key="key"
          type="button"
          class="flex items-center justify-between rounded-lg border px-3 py-2 text-left transition"
          :class="filters.content_type === key ? 'border-emerald-500/40 bg-emerald-500/10' : 'border-[#30363d] bg-[#0d1117]/60 hover:border-[#484f58]'"
          @click="filterByType(key)"
        >
          <span>
            <span class="block text-sm font-semibold text-[#e6edf3]">{{ meta.label }}</span>
            <span class="text-[11px] text-[#6e7681]">{{ meta.hint }}</span>
          </span>
          <span class="text-lg font-bold tabular-nums text-white">{{ summary.by_type[key] || 0 }}</span>
        </button>
      </div>
    </section>

    <form
      class="mb-6 overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
      @submit.prevent="applyFilters"
    >
      <div class="border-b border-[#30363d]/80 px-4 py-3 sm:px-5">
        <p class="text-sm font-semibold text-white">Filter konten</p>
        <p class="text-[11px] text-[#6e7681]">Saring judul, status approval, atau tipe produksi</p>
      </div>
      <div class="grid gap-3 p-4 sm:grid-cols-2 sm:p-5 lg:grid-cols-4 lg:items-end">
        <label class="block sm:col-span-2">
          <span class="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Kata kunci</span>
          <input
            v-model="filters.q"
            type="search"
            placeholder="Judul atau isi naskah…"
            class="w-full rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2.5 text-sm text-[#e6edf3] placeholder:text-[#6e7681] outline-none transition focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30"
          />
        </label>
        <label class="block">
          <span class="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Status</span>
          <select v-model="filters.status" :class="filterControlClass">
            <option value="">Semua status</option>
            <option v-for="(meta, key) in STATUS_META" :key="key" :value="key">{{ meta.label }}</option>
          </select>
        </label>
        <label class="block">
          <span class="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Tipe</span>
          <select v-model="filters.content_type" :class="filterControlClass">
            <option value="">Semua tipe</option>
            <option v-for="(meta, key) in TYPE_META" :key="key" :value="key">{{ meta.label }}</option>
          </select>
        </label>
        <div class="flex flex-wrap gap-2 sm:col-span-2 lg:col-span-4">
          <button type="submit" class="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-emerald-400">
            Terapkan
          </button>
          <button
            type="button"
            class="rounded-xl border border-[#30363d] px-4 py-2.5 text-sm font-medium text-[#c9d1d9] transition hover:border-[#484f58] hover:bg-[#21262d]"
            @click="resetFilters"
          >
            Reset
          </button>
        </div>
      </div>
    </form>

    <form
      v-if="showCreate && canEdit"
      class="mb-6 rounded-2xl border border-emerald-500/25 bg-[#161b22] p-5"
      @submit.prevent="createContent"
    >
      <h2 class="text-base font-semibold text-white">Produksi Konten Baru</h2>
      <p class="mt-1 text-xs text-[#8b949e]">Pilih isu, lalu susun rilis, infografis, atau video.</p>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="text-[11px] font-medium text-[#8b949e]">Isu terkait</label>
          <SearchableSelect
            v-model="form.issue_id"
            tone="dark"
            required
            :options="issueOptions"
            placeholder="— pilih isu —"
            search-placeholder="Cari judul atau risiko isu…"
          />
        </div>
        <div
          v-if="selectedIssue?.narrative_card || selectedIssue?.summary"
          class="issue-brief md:col-span-2 rounded-md border border-banten-gold/30 bg-amber-50/60 px-3 py-2 text-xs text-banten-navy"
        >
          <p class="issue-brief-title font-medium text-amber-800">Acuan Narrative Card / Brief</p>
          <p class="mt-1 whitespace-pre-wrap">
            {{ selectedIssue.narrative_card?.statement || selectedIssue.summary }}
          </p>
        </div>
        <ContentDraftFields
          v-model:content-type="form.content_type"
          v-model:title="form.title"
          v-model:body="form.body"
          v-model:media-url="form.media_url"
        />
      </div>
      <p v-if="formError" class="mt-3 text-sm text-rose-400">{{ formError }}</p>
      <button
        type="submit"
        class="mt-4 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black transition hover:bg-emerald-400 disabled:opacity-60"
        :disabled="creating"
      >
        {{ creating ? 'Menyimpan...' : 'Simpan Draft' }}
      </button>
    </form>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 4" :key="n" class="h-36 animate-pulse rounded-2xl border border-[#30363d] bg-[#161b22]" />
    </div>
    <div v-else-if="error" class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
      {{ error }}
    </div>
    <div
      v-else-if="!items.length"
      class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22]/60 px-6 py-16 text-center"
    >
      <p class="text-lg font-semibold text-white">Belum ada konten</p>
      <p class="mx-auto mt-2 max-w-md text-sm text-[#8b949e]">
        Buat draft klarifikasi dari isu yang sedang ditangani.
      </p>
    </div>
    <div v-else class="space-y-3">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        :to="`/konten/${item.id}`"
        class="group relative block overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] transition duration-200 hover:-translate-y-0.5 hover:border-emerald-500/35 hover:shadow-[0_12px_40px_-24px_rgba(16,185,129,0.45)]"
      >
        <div
          class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent"
          :class="typeOf(item).accent"
          aria-hidden="true"
        />
        <div class="px-5 py-4 pl-6">
          <div class="flex items-start justify-between gap-3">
            <h2 class="text-base font-semibold leading-snug text-white transition group-hover:text-emerald-300 sm:text-lg">
              {{ item.title }}
            </h2>
            <span
              class="shrink-0 inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold"
              :class="statusOf(item).chip"
            >
              {{ statusOf(item).label }}
            </span>
          </div>
          <div class="mt-2 flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
              {{ typeOf(item).label }}
            </span>
            <RiskBadge v-if="item.issue?.risk_level" :level="item.issue.risk_level" show-label tone="outline" />
            <span
              v-if="item.media_url"
              class="inline-flex items-center rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-sky-300"
            >
              Ada tautan media
            </span>
            <span v-if="item.updated_at" class="inline-flex items-center gap-1 text-[11px] text-[#6e7681]">
              <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l3.5 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              {{ formatDateTime(item.updated_at) }}
            </span>
          </div>
          <p class="mt-2 line-clamp-2 text-sm leading-relaxed text-[#8b949e]">
            {{ excerpt(item.body) }}
          </p>
          <p class="mt-1 truncate text-xs text-[#6e7681]">
            Isu: {{ item.issue?.title || `#${item.issue_id}` }}
          </p>
        </div>
        <div class="flex items-center justify-end border-t border-[#30363d]/80 px-5 py-2.5 pl-6">
          <span class="inline-flex items-center gap-1 text-[11px] font-medium text-[#6e7681] transition group-hover:text-emerald-400">
            Buka naskah
            <svg class="h-3.5 w-3.5 transition group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </span>
        </div>
      </RouterLink>
    </div>
    <PaginationBar :meta="meta" @update:page="onPage" />
  </div>
</template>
