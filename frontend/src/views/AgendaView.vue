<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'

const auth = useAuthStore()
const items = ref([])
const meta = ref(null)
const page = ref(1)
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)

const now = new Date()
const month = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)
const filters = ref({
  q: '',
  status: '',
  theme: '',
  channel: '',
})

const form = ref({
  title: '',
  description: '',
  theme: 'pembangunan',
  planned_date: '',
  channel: 'media',
  status: 'planned',
  target_media: '',
  notes: '',
})

const canManage = computed(() =>
  ['super_admin', 'editor', 'media_kol_admin'].includes(auth.user?.role?.code),
)

const STATUS_META = {
  planned: { label: 'Direncanakan', chip: 'border-slate-500/40 bg-slate-500/10 text-slate-300', accent: 'from-slate-400/80' },
  in_production: { label: 'Produksi', chip: 'border-amber-500/40 bg-amber-500/10 text-amber-300', accent: 'from-amber-400/80' },
  ready: { label: 'Siap tayang', chip: 'border-sky-500/40 bg-sky-500/10 text-sky-300', accent: 'from-sky-500/80' },
  published: { label: 'Terbit', chip: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300', accent: 'from-emerald-500/80' },
  cancelled: { label: 'Dibatalkan', chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300', accent: 'from-rose-500/80' },
}

const CHANNEL_LABEL = { media: 'Media', sosial: 'Sosial', both: 'Media + Sosial' }

function statusOf(item) {
  return STATUS_META[item.status] || { label: item.status, chip: 'border-[#30363d] text-[#c9d1d9]', accent: 'from-slate-500/80' }
}

const themeLabel = {
  pembangunan: 'Pembangunan',
  penghargaan: 'Penghargaan',
  sosial: 'Sosial',
  ekonomi: 'Ekonomi',
  lainnya: 'Lainnya',
}

const monthLabel = computed(() => {
  const [y, m] = month.value.split('-').map(Number)
  return new Date(y, m - 1, 1).toLocaleDateString('id-ID', { month: 'long', year: 'numeric' })
})

const grouped = computed(() => {
  const map = new Map()
  for (const item of items.value) {
    const key = item.planned_date
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(item)
  }
  return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]))
})

function shiftMonth(delta) {
  const [y, m] = month.value.split('-').map(Number)
  const d = new Date(y, m - 1 + delta, 1)
  month.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  page.value = 1
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {
      month: month.value,
      page: page.value,
      per_page: 20,
    }
    for (const [k, v] of Object.entries(filters.value)) {
      if (v) params[k] = v
    }
    const { data } = await api.get('/agenda', { params })
    items.value = data.data || []
    meta.value = data.meta || null
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat agenda'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  load()
}

function resetFilters() {
  filters.value = { q: '', status: '', theme: '', channel: '' }
  page.value = 1
  load()
}

function onPage(p) {
  page.value = p
  load()
}

function resetForm() {
  editingId.value = null
  const [y, m] = month.value.split('-')
  form.value = {
    title: '',
    description: '',
    theme: 'pembangunan',
    planned_date: `${y}-${m}-01`,
    channel: 'media',
    status: 'planned',
    target_media: '',
    notes: '',
  }
}

function editItem(item) {
  editingId.value = item.id
  form.value = {
    title: item.title,
    description: item.description || '',
    theme: item.theme || 'lainnya',
    planned_date: item.planned_date,
    channel: item.channel || 'media',
    status: item.status,
    target_media: item.target_media || '',
    notes: item.notes || '',
  }
  showForm.value = true
}

async function save() {
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      await api.patch(`/agenda/${editingId.value}`, form.value)
    } else {
      await api.post('/agenda', form.value)
    }
    showForm.value = false
    resetForm()
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan agenda'
  } finally {
    saving.value = false
  }
}

async function cancelItem(item) {
  if (!confirm(`Batalkan agenda "${item.title}"?`)) return
  await api.delete(`/agenda/${item.id}`)
  await load()
}

watch(month, () => {
  page.value = 1
  load()
})
onMounted(() => {
  resetForm()
  load()
})
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Agenda Setting</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          F.09 — Kalender konten positif (*flooding the market*)
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <div class="flex items-center gap-1 rounded-md border border-banten-navy/15 bg-white/80 p-1">
          <button type="button" class="rounded px-2 py-1 text-sm text-banten-navy hover:bg-banten-sand" @click="shiftMonth(-1)">
            ‹
          </button>
          <span class="min-w-36 px-2 text-center text-sm font-medium text-banten-navy">{{ monthLabel }}</span>
          <button type="button" class="rounded px-2 py-1 text-sm text-banten-navy hover:bg-banten-sand" @click="shiftMonth(1)">
            ›
          </button>
        </div>
        <button
          v-if="canManage"
          type="button"
          class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
          @click="showForm = !showForm; if (showForm) resetForm()"
        >
          {{ showForm ? 'Tutup' : '+ Agenda' }}
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
            placeholder="Judul, deskripsi, target media..."
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Status</label>
          <select v-model="filters.status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option v-for="s in ['planned','in_production','ready','published','cancelled']" :key="s" :value="s">
              {{ s }}
            </option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Tema</label>
          <select v-model="filters.theme" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option v-for="(label, key) in themeLabel" :key="key" :value="key">{{ label }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Kanal</label>
          <select v-model="filters.channel" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option value="media">Media</option>
            <option value="sosial">Sosial</option>
            <option value="both">Both</option>
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
      v-if="showForm && canManage"
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
      @submit.prevent="save"
    >
      <h2 class="font-display text-lg text-banten-navy">
        {{ editingId ? 'Edit Agenda' : 'Agenda Baru' }}
      </h2>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Judul</label>
          <input v-model="form.title" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
        </div>
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Deskripsi / sudut liputan</label>
          <textarea v-model="form.description" rows="2" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Tanggal rencana</label>
          <input v-model="form.planned_date" type="date" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Tema</label>
          <select v-model="form.theme" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option v-for="(label, key) in themeLabel" :key="key" :value="key">{{ label }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Kanal</label>
          <select v-model="form.channel" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="media">Media mitra</option>
            <option value="sosial">Media sosial</option>
            <option value="both">Keduanya</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Status</label>
          <select v-model="form.status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option v-for="s in ['planned','in_production','ready','published','cancelled']" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Target media</label>
          <input v-model="form.target_media" placeholder="Radar Banten, BantenNews, ..." class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
        </div>
      </div>
      <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
      <button type="submit" class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60" :disabled="saving">
        {{ saving ? 'Menyimpan...' : 'Simpan' }}
      </button>
    </form>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat kalender...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <div
      v-else-if="!items.length"
      class="rounded-xl border border-dashed border-banten-navy/20 bg-white/60 px-6 py-16 text-center"
    >
      <p class="font-display text-xl text-banten-navy">Belum ada agenda bulan ini</p>
      <p class="mt-2 text-sm text-banten-navy/60">Rencanakan konten positif untuk mengisi ruang publik.</p>
    </div>
    <div v-else class="space-y-5">
      <section v-for="[day, dayItems] in grouped" :key="day">
        <h2 class="mb-2 text-xs font-semibold uppercase tracking-wider text-[#8b949e]">
          {{ new Date(day + 'T00:00:00').toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }) }}
        </h2>
        <div class="space-y-3">
          <article
            v-for="item in dayItems"
            :key="item.id"
            class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
          >
            <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent" :class="statusOf(item).accent" aria-hidden="true" />
            <div class="px-5 py-4 pl-6">
              <div class="flex items-start justify-between gap-3">
                <h3 class="text-base font-semibold leading-snug text-white">{{ item.title }}</h3>
                <span class="shrink-0 rounded-md border px-2 py-0.5 text-[11px] font-semibold" :class="statusOf(item).chip">
                  {{ statusOf(item).label }}
                </span>
              </div>
              <div class="mt-2 flex flex-wrap gap-2">
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
                  {{ themeLabel[item.theme] || item.theme }}
                </span>
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
                  {{ CHANNEL_LABEL[item.channel] || item.channel }}
                </span>
              </div>
              <p v-if="item.description" class="mt-2 line-clamp-2 text-sm leading-relaxed text-[#8b949e]">{{ item.description }}</p>
              <p v-if="item.target_media" class="mt-1 text-xs text-[#6e7681]">Target: {{ item.target_media }}</p>
            </div>
            <div
              v-if="canManage && item.status !== 'cancelled'"
              class="flex gap-4 border-t border-[#30363d]/80 px-5 py-2.5 pl-6 text-xs font-semibold"
            >
              <button type="button" class="text-emerald-300 hover:text-emerald-200" @click="editItem(item)">Edit</button>
              <button type="button" class="text-rose-300 hover:text-rose-200" @click="cancelItem(item)">Batalkan</button>
            </div>
          </article>
        </div>
      </section>
      <PaginationBar :meta="meta" @update:page="onPage" />
    </div>
  </div>
</template>
