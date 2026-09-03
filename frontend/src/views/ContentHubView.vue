<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'
import { riskOptionLabel } from '../config/risk'

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

const statusColor = {
  draft: 'bg-slate-200 text-slate-700',
  in_review: 'bg-amber-100 text-amber-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
  published: 'bg-sky-100 text-sky-800',
}

const typeLabel = {
  text_release: 'Rilis Teks',
  infographic: 'Infografis',
  video: 'Video',
}

const canEdit = computed(() => {
  const code = auth.user?.role?.code
  return code === 'super_admin' || code === 'editor'
})

const selectedIssue = computed(() =>
  issues.value.find((i) => String(i.id) === String(form.value.issue_id)),
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

watch(
  () => selectedIssue.value,
  (issue) => {
    if (!issue || form.value.title) return
    form.value.title = `Klarifikasi: ${issue.title}`
    if (issue.narrative_card?.statement) {
      form.value.body = `Banten Meluruskan Fakta\n\n${issue.narrative_card.statement}\n\n${issue.summary || ''}`
    } else if (issue.summary && !form.value.body) {
      form.value.body = `Banten Meluruskan Fakta\n\n${issue.summary}`
    }
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
        <h1 class="font-display text-3xl text-banten-navy">Hub Konten Klarifikasi</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          F.04 — Produksi rilis, infografis, dan video dengan alur approval
        </p>
      </div>
      <button
        v-if="canEdit"
        type="button"
        class="rounded-md bg-banten-navy px-3 py-2 text-xs font-medium text-white hover:bg-banten-navy-dark"
        @click="showCreate = !showCreate"
      >
        {{ showCreate ? 'Tutup' : '+ Buat Konten' }}
      </button>
    </div>

    <form
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-4"
      @submit.prevent="applyFilters"
    >
      <div class="grid gap-3 md:grid-cols-4">
        <div class="md:col-span-2">
          <label class="text-xs font-medium text-banten-navy/70">Kata kunci</label>
          <input
            v-model="filters.q"
            type="search"
            placeholder="Judul atau isi konten..."
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Status</label>
          <select v-model="filters.status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option value="draft">Draft</option>
            <option value="in_review">Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="published">Published</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Tipe</label>
          <select v-model="filters.content_type" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option value="text_release">Rilis Teks</option>
            <option value="infographic">Infografis</option>
            <option value="video">Video</option>
          </select>
        </div>
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button type="submit" class="rounded-md bg-banten-navy px-4 py-2 text-sm text-white">Cari</button>
        <button type="button" class="rounded-md border border-banten-navy/20 px-4 py-2 text-sm text-banten-navy" @click="resetFilters">
          Reset
        </button>
      </div>
    </form>

    <form
      v-if="showCreate && canEdit"
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
      @submit.prevent="createContent"
    >
      <h2 class="font-display text-lg text-banten-navy">Produksi Konten Baru</h2>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Isu terkait</label>
          <select
            v-model="form.issue_id"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          >
            <option value="" disabled>— pilih isu —</option>
            <option v-for="i in issues" :key="i.id" :value="i.id">
              {{ riskOptionLabel(i.risk_level) }} · {{ i.title }} ({{ i.status }})
            </option>
          </select>
        </div>
        <div
          v-if="selectedIssue?.narrative_card || selectedIssue?.summary"
          class="md:col-span-2 rounded-md border border-banten-gold/30 bg-amber-50/60 px-3 py-2 text-xs text-banten-navy/80"
        >
          <p class="font-medium text-banten-navy">Acuan Narrative Card / Brief</p>
          <p class="mt-1 whitespace-pre-wrap">
            {{ selectedIssue.narrative_card?.statement || selectedIssue.summary }}
          </p>
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Tipe</label>
          <select
            v-model="form.content_type"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          >
            <option value="text_release">Rilis Teks</option>
            <option value="infographic">Infografis "Banten Meluruskan Fakta"</option>
            <option value="video">Video</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Judul</label>
          <input
            v-model="form.title"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Isi / naskah</label>
          <textarea
            v-model="form.body"
            rows="5"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
            placeholder="Tulis klarifikasi / counter-narrative..."
          />
        </div>
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">URL media (opsional)</label>
          <input
            v-model="form.media_url"
            type="url"
            placeholder="https://..."
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
      </div>
      <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
      <button
        type="submit"
        class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60"
        :disabled="creating"
      >
        {{ creating ? 'Menyimpan...' : 'Simpan Draft' }}
      </button>
    </form>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <div
      v-else-if="!items.length"
      class="rounded-xl border border-dashed border-banten-navy/20 bg-white/60 px-6 py-16 text-center"
    >
      <p class="font-display text-xl text-banten-navy">Belum ada konten</p>
      <p class="mt-2 text-sm text-banten-navy/60">Buat draft klarifikasi dari isu yang sedang ditangani.</p>
    </div>
    <div v-else class="space-y-3">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        :to="`/konten/${item.id}`"
        class="block rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4 transition hover:border-banten-gold/50"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="statusColor[item.status]">
                {{ item.status }}
              </span>
              <span class="text-xs text-banten-navy/50">{{ typeLabel[item.content_type] || item.content_type }}</span>
            </div>
            <h2 class="mt-2 font-display text-xl text-banten-navy">{{ item.title }}</h2>
            <p class="mt-1 text-sm text-banten-navy/65">
              Isu: {{ item.issue?.title || `#${item.issue_id}` }}
            </p>
          </div>
        </div>
      </RouterLink>
    </div>
    <PaginationBar :meta="meta" @update:page="onPage" />
  </div>
</template>
