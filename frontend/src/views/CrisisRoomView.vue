<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'
import RiskBadge from '../components/RiskBadge.vue'
import IssueStatusBadge from '../components/IssueStatusBadge.vue'
import { RISK_LEVELS, riskOptionLabel, riskTitle } from '../config/risk'
import { ISSUE_STATUSES, issueStatusOptionLabel } from '../config/issueStatus'

const auth = useAuthStore()
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
  source: '',
})
const form = ref({
  title: '',
  summary: '',
  why_now: '',
  risk_level: 'R2',
})

const canCreate = computed(() => {
  const code = auth.user?.role?.code
  return code === 'super_admin' || code === 'editor'
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, per_page: 10 }
    for (const [k, v] of Object.entries(filters.value)) {
      if (v) params[k] = v
    }
    const issuesRes = await api.get('/issues', { params })
    issues.value = issuesRes.data.data || []
    meta.value = issuesRes.data.meta || null
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
  filters.value = { q: '', status: '', risk_level: '', source: '' }
  page.value = 1
  load()
}

function onPage(p) {
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

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Crisis Room</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          Pusat komando isu — alert dari Mata Bathin dan input manual
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-if="canCreate"
          type="button"
          class="rounded-md bg-banten-navy px-3 py-2 text-xs font-medium text-white hover:bg-banten-navy-dark"
          @click="showCreate = !showCreate"
        >
          {{ showCreate ? 'Tutup' : '+ Input Isu Manual' }}
        </button>
      </div>
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
            placeholder="Judul, ringkasan, alert ID..."
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Status</label>
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
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button type="submit" class="rounded-md bg-banten-navy px-4 py-2 text-sm text-white">Cari</button>
        <button type="button" class="rounded-md border border-banten-navy/20 px-4 py-2 text-sm text-banten-navy" @click="resetFilters">
          Reset
        </button>
      </div>
    </form>

    <form
      v-if="showCreate"
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
      @submit.prevent="createIssue"
    >
      <h2 class="font-display text-lg text-banten-navy">Input Isu Manual</h2>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Judul</label>
          <input
            v-model="form.title"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm outline-none focus:border-banten-gold"
          />
        </div>
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Ringkasan</label>
          <textarea
            v-model="form.summary"
            rows="2"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm outline-none focus:border-banten-gold"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Why now</label>
          <input
            v-model="form.why_now"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm outline-none focus:border-banten-gold"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Risk level</label>
          <select
            v-model="form.risk_level"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm outline-none focus:border-banten-gold"
          >
            <option v-for="r in RISK_LEVELS" :key="r" :value="r" :title="riskTitle(r)">
              {{ riskOptionLabel(r) }}
            </option>
          </select>
          <p class="mt-1 text-xs text-banten-navy/55">{{ riskTitle(form.risk_level) }}</p>
        </div>
      </div>
      <p v-if="createError" class="mt-3 text-sm text-banten-red">{{ createError }}</p>
      <button
        type="submit"
        class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60"
        :disabled="creating"
      >
        {{ creating ? 'Menyimpan...' : 'Simpan Isu' }}
      </button>
    </form>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat isu...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <div
      v-else-if="!issues.length"
      class="rounded-xl border border-dashed border-banten-navy/20 bg-white/60 px-6 py-16 text-center"
    >
      <p class="font-display text-xl text-banten-navy">Belum ada isu aktif</p>
      <p class="mt-2 text-sm text-banten-navy/60">
        Alert dari Mata Bathin akan muncul di sini, atau gunakan input manual sebagai fallback.
      </p>
    </div>
    <div v-else class="space-y-3">
      <RouterLink
        v-for="issue in issues"
        :key="issue.id"
        :to="`/issues/${issue.id}`"
        class="block rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4 transition hover:border-banten-gold/50 hover:shadow-sm"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <RiskBadge :level="issue.risk_level" show-label />
            </div>
            <h2 class="mt-2 font-display text-xl text-banten-navy">{{ issue.title }}</h2>
            <p class="mt-1 line-clamp-2 text-sm text-banten-navy/70">
              {{ issue.summary || issue.why_now || 'Tidak ada ringkasan' }}
            </p>
          </div>
          <IssueStatusBadge :status="issue.status" />
        </div>
      </RouterLink>
    </div>
    <PaginationBar :meta="meta" @update:page="onPage" />
  </div>
</template>
