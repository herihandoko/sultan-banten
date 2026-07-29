<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import PaginationBar from '../components/PaginationBar.vue'

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

const riskColor = {
  R0: 'bg-slate-200 text-slate-700',
  R1: 'bg-sky-100 text-sky-800',
  R2: 'bg-amber-100 text-amber-800',
  R3: 'bg-orange-100 text-orange-800',
  R4: 'bg-red-100 text-red-800',
  R5: 'bg-banten-red text-white',
}

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
            <option v-for="s in ['open','validating','producing','approved','disseminated','closed']" :key="s" :value="s">
              {{ s }}
            </option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Risk</label>
          <select v-model="filters.risk_level" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option v-for="r in ['R0','R1','R2','R3','R4','R5']" :key="r" :value="r">{{ r }}</option>
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
          class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-10 text-center text-sm text-banten-navy/60"
        >
          Tidak ada isu yang cocok.
        </div>
        <div v-else class="space-y-3">
          <article
            v-for="issue in issues"
            :key="issue.id"
            class="rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4"
          >
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="riskColor[issue.risk_level]">
                    {{ issue.risk_level }}
                  </span>
                  <span class="rounded-md bg-banten-sand px-2 py-0.5 text-xs text-banten-navy">
                    {{ issue.status }}
                  </span>
                  <span class="text-xs uppercase text-banten-navy/45">{{ issue.source }}</span>
                </div>
                <h3 class="mt-2 font-display text-xl text-banten-navy">
                  <RouterLink :to="`/issues/${issue.id}`" class="hover:text-banten-gold">
                    {{ issue.title }}
                  </RouterLink>
                </h3>
                <p class="mt-1 line-clamp-2 text-sm text-banten-navy/70">
                  {{ issue.summary || issue.why_now || '—' }}
                </p>
                <p class="mt-2 text-xs text-banten-navy/55">
                  Evidence {{ issue.archive.evidence_count }} ·
                  Validasi {{ issue.archive.validated_count }}/{{ issue.archive.validation_count }} ·
                  Konten {{ issue.archive.content_approved }}/{{ issue.archive.content_count }} ·
                  Blast {{ issue.archive.blast_count }}
                </p>
              </div>
              <button
                type="button"
                class="text-xs text-banten-gold hover:underline"
                @click="toggleTimeline(issue.id)"
              >
                {{ expandedId === issue.id ? 'Tutup timeline' : 'Lihat timeline' }}
              </button>
            </div>
            <ol
              v-if="expandedId === issue.id"
              class="mt-4 space-y-2 border-t border-banten-navy/10 pt-3"
            >
              <li
                v-for="(ev, idx) in issue.archive.timeline"
                :key="idx"
                class="flex gap-3 text-xs text-banten-navy/70"
              >
                <span class="w-40 shrink-0 text-banten-navy/40">{{ ev.at }}</span>
                <span>{{ ev.label }}</span>
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
          class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-10 text-center text-sm text-banten-navy/60"
        >
          Tidak ada konten yang cocok.
        </div>
        <div v-else class="space-y-2">
          <RouterLink
            v-for="c in contents"
            :key="c.id"
            :to="`/konten/${c.id}`"
            class="block rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4 transition hover:border-banten-gold/40"
          >
            <div class="flex flex-wrap items-center gap-2 text-xs">
              <span class="rounded bg-banten-sand px-2 py-0.5 text-banten-navy">{{ c.status }}</span>
              <span class="text-banten-navy/45">{{ c.content_type }}</span>
            </div>
            <p class="mt-2 font-display text-lg text-banten-navy">{{ c.title }}</p>
            <p class="mt-1 text-xs text-banten-navy/55">
              Isu: {{ c.issue_title || `#${c.issue_id}` }}
              <span v-if="c.issue_risk_level"> · {{ c.issue_risk_level }}</span>
            </p>
          </RouterLink>
        </div>
        <PaginationBar :meta="meta.contents" @update:page="onContentsPage" />
      </section>
    </template>
  </div>
</template>
