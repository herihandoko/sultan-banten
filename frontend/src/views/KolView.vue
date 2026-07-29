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

const canManage = computed(() =>
  ['super_admin', 'media_kol_admin'].includes(auth.user?.role?.code),
)

const contractColor = {
  prospect: 'bg-slate-200 text-slate-700',
  active: 'bg-emerald-100 text-emerald-800',
  expired: 'bg-amber-100 text-amber-800',
  terminated: 'bg-red-100 text-red-800',
}

const campaignColor = {
  planned: 'bg-slate-200 text-slate-700',
  in_progress: 'bg-amber-100 text-amber-800',
  published: 'bg-sky-100 text-sky-800',
  completed: 'bg-emerald-100 text-emerald-800',
  cancelled: 'bg-red-100 text-red-800',
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
    const [pRes, pAllRes, cRes] = await Promise.all([
      api.get('/kol/partners', { params: { page: partnersPage.value, per_page: 10 } }),
      api.get('/kol/partners', { params: { per_page: 200 } }),
      api.get('/kol/campaigns', { params: { page: campaignsPage.value, per_page: 10 } }),
    ])
    partners.value = pRes.data.data || []
    partnersMeta.value = pRes.data.meta || null
    partnersAll.value = pAllRes.data.data || []
    campaigns.value = cRes.data.data || []
    campaignsMeta.value = cRes.data.meta || null
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat data KOL'
  } finally {
    loading.value = false
  }
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
    formError.value = err.response?.data?.error || 'Gagal menyimpan KOL'
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
        <h1 class="font-display text-3xl text-banten-navy">KOL Management</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          F.12 Direktori KOL · F.13 Campaign Tracker
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
          {{ showForm ? 'Tutup' : '+ Tambah KOL' }}
        </button>
      </div>

      <form
        v-if="showForm && canManage"
        class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
        @submit.prevent="savePartner"
      >
        <h2 class="font-display text-lg text-banten-navy">
          {{ editingId ? 'Edit KOL' : 'KOL Baru' }}
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
        Belum ada KOL.
      </div>
      <div v-else class="grid gap-3 md:grid-cols-2">
        <article
          v-for="p in partners"
          :key="p.id"
          class="rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4"
        >
          <div class="flex items-start justify-between gap-2">
            <div>
              <p class="font-display text-lg text-banten-navy">{{ p.name }}</p>
              <p class="text-xs text-banten-navy/55">{{ p.platform }} · {{ p.handle || '—' }}</p>
            </div>
            <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="contractColor[p.contract_status]">
              {{ p.contract_status }}
            </span>
          </div>
          <p class="mt-3 text-sm text-banten-navy/75">
            {{ formatNum(p.followers) }} followers · ER {{ p.engagement_rate }}%
          </p>
          <p v-if="p.topics" class="mt-1 text-xs text-banten-navy/55">{{ p.topics }}</p>
          <div class="mt-3 flex items-center justify-between text-xs">
            <span class="text-banten-navy/50">{{ p.campaign_count || 0 }} campaign</span>
            <button
              v-if="canManage"
              type="button"
              class="text-banten-gold hover:underline"
              @click="editPartner(p)"
            >
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
            <label class="text-sm font-medium text-banten-navy">KOL</label>
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
        Belum ada campaign KOL.
      </div>
      <div v-else class="space-y-3">
        <article
          v-for="c in campaigns"
          :key="c.id"
          class="rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="campaignColor[c.status]">
                  {{ c.status }}
                </span>
                <span class="text-xs text-banten-navy/50">{{ c.budget_status }}</span>
              </div>
              <h2 class="mt-2 font-display text-xl text-banten-navy">{{ c.title }}</h2>
              <p class="mt-1 text-sm text-banten-navy/65">
                {{ c.kol?.name || `KOL #${c.kol_id}` }} · {{ c.kol?.platform }} {{ c.kol?.handle }}
              </p>
              <p class="mt-2 text-xs text-banten-navy/55">
                {{ formatNum(c.views) }} views · {{ formatNum(c.likes) }} likes · {{ formatNum(c.comments) }} comments
                · {{ formatMoney(c.budget) }}
              </p>
              <a
                v-if="c.deliverable_url"
                :href="c.deliverable_url"
                target="_blank"
                rel="noopener"
                class="mt-2 inline-block text-xs text-banten-gold hover:underline"
              >
                Lihat deliverable
              </a>
            </div>
            <button
              v-if="canManage"
              type="button"
              class="text-xs text-banten-gold hover:underline"
              @click="editCampaign(c)"
            >
              Update
            </button>
          </div>
        </article>
      </div>
      <PaginationBar :meta="campaignsMeta" @update:page="onCampaignsPage" />
    </template>
  </div>
</template>
