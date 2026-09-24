<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'

const auth = useAuthStore()
const tab = ref('partners') // partners | campaigns
const partners = ref([])
const partnersAll = ref([])
const partnersMeta = ref(null)
const partnersPage = ref(1)
const campaigns = ref([])
const campaignsMeta = ref(null)
const campaignsPage = ref(1)
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)

const partnerForm = ref({
  name: '',
  platform: 'instagram',
  handle: '',
  followers: 0,
  engagement_rate: 0,
  topics: '',
  contract_status: 'prospect',
  notes: '',
  is_active: true,
})

const showCampaignForm = ref(false)
const campaignForm = ref({
  kol_id: '',
  title: '',
  deliverable_url: '',
  scheduled_at: '',
  budget: '',
  budget_status: 'planned',
  status: 'planned',
  notes: '',
  views: 0,
  likes: 0,
  comments: 0,
})
const editingCampaignId = ref(null)
const filters = ref({
  q: '',
  active: '',
  platform: '',
  contract_status: '',
  campaign_status: '',
  budget_status: '',
})

const canManage = computed(() =>
  ['super_admin', 'media_kol_admin'].includes(auth.user?.role?.code),
)

const CONTRACT_META = {
  prospect: { label: 'Prospek', chip: 'border-slate-500/40 bg-slate-500/10 text-slate-300', accent: 'from-slate-400/80' },
  active: { label: 'Aktif', chip: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300', accent: 'from-emerald-500/80' },
  expired: { label: 'Habis', chip: 'border-amber-500/40 bg-amber-500/10 text-amber-300', accent: 'from-amber-400/80' },
  terminated: { label: 'Dihentikan', chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300', accent: 'from-rose-500/80' },
}

const CAMPAIGN_META = {
  planned: { label: 'Direncanakan', chip: 'border-slate-500/40 bg-slate-500/10 text-slate-300', accent: 'from-slate-400/80' },
  in_progress: { label: 'Berjalan', chip: 'border-amber-500/40 bg-amber-500/10 text-amber-300', accent: 'from-amber-400/80' },
  published: { label: 'Tayang', chip: 'border-sky-500/40 bg-sky-500/10 text-sky-300', accent: 'from-sky-500/80' },
  completed: { label: 'Selesai', chip: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300', accent: 'from-emerald-500/80' },
  cancelled: { label: 'Dibatalkan', chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300', accent: 'from-rose-500/80' },
}

const BUDGET_LABEL = { planned: 'Anggaran rencana', approved: 'Anggaran disetujui', paid: 'Sudah dibayar', cancelled: 'Anggaran batal' }

function contractOf(partner) {
  return CONTRACT_META[partner.contract_status] || { label: partner.contract_status, chip: 'border-[#30363d] text-[#c9d1d9]', accent: 'from-slate-500/80' }
}

function campaignOf(item) {
  return CAMPAIGN_META[item.status] || { label: item.status, chip: 'border-[#30363d] text-[#c9d1d9]', accent: 'from-slate-500/80' }
}

function formatNum(n) {
  return new Intl.NumberFormat('id-ID').format(n || 0)
}

function formatMoney(n) {
  if (n == null || n === '') return '—'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(n)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const partnerParams = { page: partnersPage.value, per_page: 10 }
    if (filters.value.q) partnerParams.q = filters.value.q
    if (filters.value.active) partnerParams.active = filters.value.active
    if (filters.value.platform) partnerParams.platform = filters.value.platform
    if (filters.value.contract_status) partnerParams.contract_status = filters.value.contract_status
    const campaignParams = { page: campaignsPage.value, per_page: 10 }
    if (filters.value.q) campaignParams.q = filters.value.q
    if (filters.value.campaign_status) campaignParams.status = filters.value.campaign_status
    if (filters.value.budget_status) campaignParams.budget_status = filters.value.budget_status
    const [pRes, pAllRes, cRes] = await Promise.all([
      api.get('/kol/partners', { params: partnerParams }),
      api.get('/kol/partners', { params: { per_page: 200 } }),
      api.get('/kol/campaigns', { params: campaignParams }),
    ])
    partners.value = pRes.data.data || []
    partnersMeta.value = pRes.data.meta || null
    partnersAll.value = pAllRes.data.data || []
    campaigns.value = cRes.data.data || []
    campaignsMeta.value = cRes.data.meta || null
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat data influencer'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  partnersPage.value = 1
  campaignsPage.value = 1
  load()
}

function resetFilters() {
  filters.value = {
    q: '',
    active: '',
    platform: '',
    contract_status: '',
    campaign_status: '',
    budget_status: '',
  }
  partnersPage.value = 1
  campaignsPage.value = 1
  load()
}

function onPartnersPage(p) {
  partnersPage.value = p
  load()
}
function onCampaignsPage(p) {
  campaignsPage.value = p
  load()
}

function resetPartnerForm() {
  editingId.value = null
  partnerForm.value = {
    name: '',
    platform: 'instagram',
    handle: '',
    followers: 0,
    engagement_rate: 0,
    topics: '',
    contract_status: 'prospect',
    notes: '',
    is_active: true,
  }
}

function editPartner(p) {
  editingId.value = p.id
  partnerForm.value = { ...p }
  showForm.value = true
  tab.value = 'partners'
}

async function savePartner() {
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      ...partnerForm.value,
      followers: Number(partnerForm.value.followers) || 0,
      engagement_rate: Number(partnerForm.value.engagement_rate) || 0,
    }
    if (editingId.value) {
      await api.patch(`/kol/partners/${editingId.value}`, payload)
    } else {
      await api.post('/kol/partners', payload)
    }
    showForm.value = false
    resetPartnerForm()
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan influencer'
  } finally {
    saving.value = false
  }
}

function resetCampaignForm() {
  editingCampaignId.value = null
  campaignForm.value = {
    kol_id: partnersAll.value[0]?.id ? String(partnersAll.value[0].id) : '',
    title: '',
    deliverable_url: '',
    scheduled_at: '',
    budget: '',
    budget_status: 'planned',
    status: 'planned',
    notes: '',
    views: 0,
    likes: 0,
    comments: 0,
  }
}

function editCampaign(c) {
  editingCampaignId.value = c.id
  campaignForm.value = {
    kol_id: String(c.kol_id),
    title: c.title,
    deliverable_url: c.deliverable_url || '',
    scheduled_at: c.scheduled_at ? c.scheduled_at.slice(0, 16) : '',
    budget: c.budget ?? '',
    budget_status: c.budget_status || 'planned',
    status: c.status,
    notes: c.notes || '',
    views: c.views || 0,
    likes: c.likes || 0,
    comments: c.comments || 0,
  }
  showCampaignForm.value = true
  tab.value = 'campaigns'
}

async function saveCampaign() {
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      ...campaignForm.value,
      kol_id: Number(campaignForm.value.kol_id),
      budget: campaignForm.value.budget === '' ? null : Number(campaignForm.value.budget),
      views: Number(campaignForm.value.views) || 0,
      likes: Number(campaignForm.value.likes) || 0,
      comments: Number(campaignForm.value.comments) || 0,
      scheduled_at: campaignForm.value.scheduled_at
        ? new Date(campaignForm.value.scheduled_at).toISOString()
        : null,
    }
    if (editingCampaignId.value) {
      await api.patch(`/kol/campaigns/${editingCampaignId.value}`, payload)
    } else {
      await api.post('/kol/campaigns', payload)
    }
    showCampaignForm.value = false
    resetCampaignForm()
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan campaign'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Influencer (KOL)</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          Direktori KOL dan campaign tracker
        </p>
      </div>
      <div class="flex gap-1 rounded-md border border-banten-navy/15 bg-white/70 p-1 text-xs">
        <button
          v-for="t in [
            { key: 'partners', label: 'Direktori KOL' },
            { key: 'campaigns', label: 'Campaign' },
          ]"
          :key="t.key"
          type="button"
          class="rounded px-3 py-1.5"
          :class="tab === t.key ? 'bg-banten-navy text-white' : 'text-banten-navy/70'"
          @click="tab = t.key"
        >
          {{ t.label }}
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
            :placeholder="tab === 'partners' ? 'Nama, handle, topik...' : 'Judul campaign, catatan...'"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <template v-if="tab === 'partners'">
          <div>
            <label class="text-xs font-medium text-banten-navy/70">Platform</label>
            <select v-model="filters.platform" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="">Semua</option>
              <option v-for="p in ['instagram','tiktok','youtube','twitter','facebook','other']" :key="p" :value="p">
                {{ p }}
              </option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium text-banten-navy/70">Kontrak</label>
            <select v-model="filters.contract_status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="">Semua</option>
              <option v-for="s in ['prospect','active','expired','terminated']" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium text-banten-navy/70">Status</label>
            <select v-model="filters.active" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="">Semua</option>
              <option value="1">Aktif</option>
              <option value="0">Nonaktif</option>
            </select>
          </div>
        </template>
        <template v-else>
          <div>
            <label class="text-xs font-medium text-banten-navy/70">Status campaign</label>
            <select v-model="filters.campaign_status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="">Semua</option>
              <option v-for="s in ['planned','in_progress','published','completed','cancelled']" :key="s" :value="s">
                {{ s }}
              </option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium text-banten-navy/70">Budget</label>
            <select v-model="filters.budget_status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="">Semua</option>
              <option v-for="s in ['planned','approved','paid','cancelled']" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
        </template>
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button type="submit" class="rounded-md bg-banten-navy px-4 py-2 text-sm text-white">Cari</button>
        <button type="button" class="rounded-md border border-banten-navy/20 px-4 py-2 text-sm text-banten-navy" @click="resetFilters">
          Reset
        </button>
      </div>
    </form>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <template v-else-if="tab === 'partners'">
      <div class="mb-4 flex justify-end">
        <button
          v-if="canManage"
          type="button"
          class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
          @click="showForm = !showForm; if (!showForm) resetPartnerForm()"
        >
          {{ showForm ? 'Tutup' : '+ Tambah Influencer' }}
        </button>
      </div>

      <form
        v-if="showForm && canManage"
        class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
        @submit.prevent="savePartner"
      >
        <h2 class="font-display text-lg text-banten-navy">
          {{ editingId ? 'Edit Influencer' : 'Influencer baru' }}
        </h2>
        <div class="mt-4 grid gap-3 md:grid-cols-2">
          <div>
            <label class="text-sm font-medium text-banten-navy">Nama</label>
            <input v-model="partnerForm.name" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Handle</label>
            <input v-model="partnerForm.handle" placeholder="@username" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Platform</label>
            <select v-model="partnerForm.platform" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option v-for="p in ['instagram','tiktok','youtube','twitter','facebook','other']" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Status kontrak</label>
            <select v-model="partnerForm.contract_status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="prospect">prospect</option>
              <option value="active">active</option>
              <option value="expired">expired</option>
              <option value="terminated">terminated</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Followers</label>
            <input v-model="partnerForm.followers" type="number" min="0" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Engagement rate (%)</label>
            <input v-model="partnerForm.engagement_rate" type="number" step="0.01" min="0" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-2">
            <label class="text-sm font-medium text-banten-navy">Topik</label>
            <input v-model="partnerForm.topics" placeholder="pemerintahan, wisata, ..." class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
        </div>
        <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
        <button type="submit" class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60" :disabled="saving">
          {{ saving ? 'Menyimpan...' : 'Simpan' }}
        </button>
      </form>

      <div v-if="!partners.length" class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-12 text-center text-sm text-banten-navy/60">
        Belum ada influencer.
      </div>
      <div v-else class="grid gap-3 md:grid-cols-2">
        <article
          v-for="p in partners"
          :key="p.id"
          class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
        >
          <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent" :class="contractOf(p).accent" aria-hidden="true" />
          <div class="px-5 py-4 pl-6">
            <div class="flex items-start justify-between gap-2">
              <h2 class="text-base font-semibold text-white">{{ p.name }}</h2>
              <span class="shrink-0 rounded-md border px-2 py-0.5 text-[11px] font-semibold" :class="contractOf(p).chip">
                {{ contractOf(p).label }}
              </span>
            </div>
            <p class="mt-1 text-xs text-[#8b949e]">{{ p.platform }} · {{ p.handle || 'tanpa handle' }}</p>
            <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ formatNum(p.followers) }} followers</span>
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">ER {{ p.engagement_rate }}%</span>
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ p.campaign_count || 0 }} campaign</span>
            </div>
            <p v-if="p.topics" class="mt-2 line-clamp-2 text-xs text-[#6e7681]">{{ p.topics }}</p>
          </div>
          <div v-if="canManage" class="border-t border-[#30363d]/80 px-5 py-2.5 pl-6">
            <button type="button" class="text-xs font-semibold text-emerald-300 hover:text-emerald-200" @click="editPartner(p)">
              Edit
            </button>
          </div>
        </article>
      </div>
      <PaginationBar :meta="partnersMeta" @update:page="onPartnersPage" />
    </template>

    <template v-else>
      <div class="mb-4 flex justify-end">
        <button
          v-if="canManage"
          type="button"
          class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
          @click="showCampaignForm = !showCampaignForm; if (showCampaignForm) resetCampaignForm()"
        >
          {{ showCampaignForm ? 'Tutup' : '+ Campaign' }}
        </button>
      </div>

      <form
        v-if="showCampaignForm && canManage"
        class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
        @submit.prevent="saveCampaign"
      >
        <h2 class="font-display text-lg text-banten-navy">
          {{ editingCampaignId ? 'Update Campaign' : 'Campaign Baru' }}
        </h2>
        <div class="mt-4 grid gap-3 md:grid-cols-2">
          <div>
            <label class="text-sm font-medium text-banten-navy">Influencer</label>
            <select v-model="campaignForm.kol_id" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option v-for="p in partnersAll" :key="p.id" :value="p.id">{{ p.name }} · {{ p.platform }}</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Status</label>
            <select v-model="campaignForm.status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option v-for="s in ['planned','in_progress','published','completed','cancelled']" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="text-sm font-medium text-banten-navy">Judul</label>
            <input v-model="campaignForm.title" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Deliverable URL</label>
            <input v-model="campaignForm.deliverable_url" type="url" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Jadwal tayang</label>
            <input v-model="campaignForm.scheduled_at" type="datetime-local" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Anggaran (Rp)</label>
            <input v-model="campaignForm.budget" type="number" min="0" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Status anggaran</label>
            <select v-model="campaignForm.budget_status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option v-for="s in ['planned','approved','paid','cancelled']" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Views</label>
            <input v-model="campaignForm.views" type="number" min="0" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Likes / Comments</label>
            <div class="mt-1 grid grid-cols-2 gap-2">
              <input v-model="campaignForm.likes" type="number" min="0" placeholder="likes" class="rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
              <input v-model="campaignForm.comments" type="number" min="0" placeholder="comments" class="rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
          </div>
        </div>
        <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
        <button type="submit" class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60" :disabled="saving">
          {{ saving ? 'Menyimpan...' : 'Simpan Campaign' }}
        </button>
      </form>

      <div v-if="!campaigns.length" class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-12 text-center text-sm text-banten-navy/60">
        Belum ada campaign.
      </div>
      <div v-else class="space-y-3">
        <article
          v-for="c in campaigns"
          :key="c.id"
          class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
        >
          <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent" :class="campaignOf(c).accent" aria-hidden="true" />
          <div class="px-5 py-4 pl-6">
            <div class="flex items-start justify-between gap-3">
              <h2 class="text-base font-semibold leading-snug text-white">{{ c.title }}</h2>
              <span class="shrink-0 rounded-md border px-2 py-0.5 text-[11px] font-semibold" :class="campaignOf(c).chip">
                {{ campaignOf(c).label }}
              </span>
            </div>
            <p class="mt-1 text-sm text-[#8b949e]">
              {{ c.kol?.name || `Influencer #${c.kol_id}` }} · {{ c.kol?.platform }} {{ c.kol?.handle }}
            </p>
            <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ formatNum(c.views) }} views</span>
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ formatNum(c.likes) }} likes</span>
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ formatNum(c.comments) }} komentar</span>
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ formatMoney(c.budget) }}</span>
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-amber-200">{{ BUDGET_LABEL[c.budget_status] || c.budget_status }}</span>
            </div>
            <a
              v-if="c.deliverable_url"
              :href="c.deliverable_url"
              target="_blank"
              rel="noopener"
              class="mt-2 inline-flex text-xs font-semibold text-sky-300 hover:text-emerald-300"
            >
              Lihat deliverable
            </a>
          </div>
          <div v-if="canManage" class="border-t border-[#30363d]/80 px-5 py-2.5 pl-6">
            <button type="button" class="text-xs font-semibold text-emerald-300 hover:text-emerald-200" @click="editCampaign(c)">
              Update
            </button>
          </div>
        </article>
      </div>
      <PaginationBar :meta="campaignsMeta" @update:page="onCampaignsPage" />
    </template>
  </div>
</template>
