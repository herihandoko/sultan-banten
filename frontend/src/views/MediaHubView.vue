<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'

const auth = useAuthStore()
const tab = ref('partners') // partners | blast | logs | sla
const partners = ref([])
const partnersAll = ref([])
const partnersMeta = ref(null)
const partnersPage = ref(1)
const readyContent = ref([])
const blasts = ref([])
const blastsMeta = ref(null)
const blastsPage = ref(1)
const slaLogs = ref([])
const slaMeta = ref(null)
const slaPage = ref(1)
const slaRanking = ref([])
const slaMinutes = ref(60)
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)
const showSlaForm = ref(false)

const partnerForm = ref({
  name: '',
  editor_name: '',
  whatsapp: '',
  email: '',
  coverage_area: '',
  crisis_channel: '',
  notes: '',
  is_active: true,
})

const blastForm = ref({
  content_id: '',
  channel: 'both',
  partner_ids: [],
})
const blasting = ref(false)
const blastResult = ref(null)
const selectAll = ref(true)
const filters = ref({
  q: '',
  active: '',
  blast_status: '',
})

const slaForm = ref({
  media_partner_id: '',
  blast_log_id: '',
  published_at: '',
  response_minutes: '',
  content_match: true,
  notes: '',
})

const canManage = computed(() =>
  ['super_admin', 'editor', 'media_kol_admin'].includes(auth.user?.role?.code),
)

const statusColor = {
  sent: 'bg-emerald-100 text-emerald-800',
  partial: 'bg-amber-100 text-amber-800',
  failed: 'bg-red-100 text-red-800',
  pending: 'bg-slate-200 text-slate-700',
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const partnerParams = { page: partnersPage.value, per_page: 10 }
    if (filters.value.q) partnerParams.q = filters.value.q
    if (filters.value.active) partnerParams.active = filters.value.active
    const blastParams = { page: blastsPage.value, per_page: 10 }
    if (filters.value.q) blastParams.q = filters.value.q
    if (filters.value.blast_status) blastParams.status = filters.value.blast_status
    const reqs = [
      api.get('/media/partners', { params: partnerParams }),
      api.get('/media/partners', { params: { active: '1', per_page: 200 } }),
      api.get('/media/blasts', { params: blastParams }),
      api.get('/media/sla', { params: { page: slaPage.value, per_page: 10 } }),
      api.get('/media/sla/ranking'),
    ]
    if (canManage.value) reqs.push(api.get('/media/blast-ready-content'))
    const [pRes, pAllRes, bRes, slaRes, rankRes, cRes] = await Promise.all(reqs)
    partners.value = pRes.data.data || []
    partnersMeta.value = pRes.data.meta || null
    partnersAll.value = pAllRes.data.data || []
    blasts.value = bRes.data.data || []
    blastsMeta.value = bRes.data.meta || null
    slaLogs.value = slaRes.data.data || []
    slaMeta.value = slaRes.data.meta || null
    slaMinutes.value = slaRes.data.sla_minutes || 60
    slaRanking.value = rankRes.data.data || []
    if (cRes) {
      readyContent.value = cRes.data.data || []
      if (!blastForm.value.content_id && readyContent.value.length) {
        blastForm.value.content_id = String(readyContent.value[0].id)
      }
    }
    if (selectAll.value) {
      blastForm.value.partner_ids = partnersAll.value.filter((p) => p.is_active).map((p) => p.id)
    }
    if (!slaForm.value.media_partner_id && partnersAll.value.length) {
      slaForm.value.media_partner_id = String(partnersAll.value[0].id)
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat Media Hub'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  partnersPage.value = 1
  blastsPage.value = 1
  load()
}

function resetFilters() {
  filters.value = { q: '', active: '', blast_status: '' }
  partnersPage.value = 1
  blastsPage.value = 1
  load()
}

function onPartnersPage(p) {
  partnersPage.value = p
  load()
}
function onBlastsPage(p) {
  blastsPage.value = p
  load()
}
function onSlaPage(p) {
  slaPage.value = p
  load()
}

function resetPartnerForm() {
  editingId.value = null
  partnerForm.value = {
    name: '',
    editor_name: '',
    whatsapp: '',
    email: '',
    coverage_area: '',
    crisis_channel: '',
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
    if (editingId.value) {
      await api.patch(`/media/partners/${editingId.value}`, partnerForm.value)
    } else {
      await api.post('/media/partners', partnerForm.value)
    }
    showForm.value = false
    resetPartnerForm()
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan mitra'
  } finally {
    saving.value = false
  }
}

async function deactivate(p) {
  if (!confirm(`Nonaktifkan ${p.name}?`)) return
  await api.delete(`/media/partners/${p.id}`)
  await load()
}

function toggleSelectAll() {
  selectAll.value = !selectAll.value
  blastForm.value.partner_ids = selectAll.value
    ? partnersAll.value.filter((p) => p.is_active).map((p) => p.id)
    : []
}

function togglePartner(id) {
  const set = new Set(blastForm.value.partner_ids)
  if (set.has(id)) set.delete(id)
  else set.add(id)
  blastForm.value.partner_ids = [...set]
  selectAll.value =
    blastForm.value.partner_ids.length === partnersAll.value.filter((p) => p.is_active).length
}

async function runBlast() {
  blasting.value = true
  formError.value = ''
  blastResult.value = null
  try {
    const { data } = await api.post('/media/blast', {
      content_id: Number(blastForm.value.content_id),
      channel: blastForm.value.channel,
      partner_ids: blastForm.value.partner_ids,
    })
    blastResult.value = data.data
    tab.value = 'logs'
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal mengirim blast'
  } finally {
    blasting.value = false
  }
}

async function saveSla() {
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      media_partner_id: Number(slaForm.value.media_partner_id),
      blast_log_id: slaForm.value.blast_log_id
        ? Number(slaForm.value.blast_log_id)
        : null,
      content_match: slaForm.value.content_match,
      notes: slaForm.value.notes || null,
    }
    if (slaForm.value.published_at) {
      payload.published_at = new Date(slaForm.value.published_at).toISOString()
    }
    if (slaForm.value.response_minutes !== '' && slaForm.value.response_minutes != null) {
      payload.response_minutes = Number(slaForm.value.response_minutes)
    }
    await api.post('/media/sla', payload)
    showSlaForm.value = false
    slaForm.value = {
      media_partner_id: partnersAll.value[0] ? String(partnersAll.value[0].id) : '',
      blast_log_id: '',
      published_at: '',
      response_minutes: '',
      content_match: true,
      notes: '',
    }
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal mencatat SLA'
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
        <h1 class="font-display text-3xl text-banten-navy">Media Hub</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          F.06 Mitra · F.07 SLA · F.08 Media Blast
        </p>
      </div>
      <div class="flex gap-1 rounded-md border border-banten-navy/15 bg-white/70 p-1 text-xs">
        <button
          v-for="t in [
            { key: 'partners', label: 'Media Mitra' },
            { key: 'blast', label: 'Media Blast' },
            { key: 'sla', label: 'SLA' },
            { key: 'logs', label: 'Riwayat Blast' },
          ]"
          :key="t.key"
          type="button"
          class="rounded px-3 py-1.5 transition"
          :class="tab === t.key ? 'bg-banten-navy text-white' : 'text-banten-navy/70 hover:bg-banten-sand'"
          @click="tab = t.key"
        >
          {{ t.label }}
        </button>
      </div>
    </div>

    <form
      v-if="tab === 'partners' || tab === 'logs'"
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-4"
      @submit.prevent="applyFilters"
    >
      <div class="grid gap-3 md:grid-cols-4">
        <div class="md:col-span-2">
          <label class="text-xs font-medium text-banten-navy/70">Kata kunci</label>
          <input
            v-model="filters.q"
            type="search"
            :placeholder="tab === 'partners' ? 'Nama media, editor, wilayah...' : 'Judul konten, kanal...'"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div v-if="tab === 'partners'">
          <label class="text-xs font-medium text-banten-navy/70">Status mitra</label>
          <select v-model="filters.active" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option value="1">Aktif</option>
            <option value="0">Nonaktif</option>
          </select>
        </div>
        <div v-if="tab === 'logs'">
          <label class="text-xs font-medium text-banten-navy/70">Status blast</label>
          <select v-model="filters.blast_status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option value="sent">Sent</option>
            <option value="partial">Partial</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
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

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <template v-else>
      <!-- Partners -->
      <div v-if="tab === 'partners'">
        <div class="mb-4 flex justify-end">
          <button
            v-if="canManage"
            type="button"
            class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
            @click="showForm = !showForm; if (!showForm) resetPartnerForm()"
          >
            {{ showForm ? 'Tutup' : '+ Tambah Mitra' }}
          </button>
        </div>

        <form
          v-if="showForm && canManage"
          class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
          @submit.prevent="savePartner"
        >
          <h2 class="font-display text-lg text-banten-navy">
            {{ editingId ? 'Edit Media Mitra' : 'Media Mitra Baru' }}
          </h2>
          <div class="mt-4 grid gap-3 md:grid-cols-2">
            <div>
              <label class="text-sm font-medium text-banten-navy">Nama media</label>
              <input v-model="partnerForm.name" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Pemred / kontak</label>
              <input v-model="partnerForm.editor_name" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">WhatsApp</label>
              <input v-model="partnerForm.whatsapp" placeholder="62812..." class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Email</label>
              <input v-model="partnerForm.email" type="email" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Wilayah coverage</label>
              <input v-model="partnerForm.coverage_area" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Kanal darurat krisis</label>
              <input v-model="partnerForm.crisis_channel" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
          </div>
          <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
          <button type="submit" class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </form>

        <div v-if="!partners.length" class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-12 text-center text-sm text-banten-navy/60">
          Belum ada media mitra.
        </div>
        <div v-else class="overflow-x-auto rounded-xl border border-banten-navy/10 bg-white/80">
          <table class="min-w-full text-left text-sm">
            <thead class="border-b border-banten-navy/10 bg-banten-sand/50 text-xs uppercase text-banten-navy/60">
              <tr>
                <th class="px-4 py-3">Media</th>
                <th class="px-4 py-3">Kontak</th>
                <th class="px-4 py-3">Coverage</th>
                <th class="px-4 py-3">Status</th>
                <th v-if="canManage" class="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in partners" :key="p.id" class="border-b border-banten-navy/5">
                <td class="px-4 py-3">
                  <p class="font-medium text-banten-navy">{{ p.name }}</p>
                  <p class="text-xs text-banten-navy/55">{{ p.editor_name || '—' }}</p>
                </td>
                <td class="px-4 py-3 text-xs text-banten-navy/70">
                  <p>WA: {{ p.whatsapp || '—' }}</p>
                  <p>{{ p.email || '—' }}</p>
                </td>
                <td class="px-4 py-3 text-xs text-banten-navy/70">{{ p.coverage_area || '—' }}</td>
                <td class="px-4 py-3">
                  <span
                    class="rounded px-2 py-0.5 text-xs font-semibold"
                    :class="p.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-600'"
                  >
                    {{ p.is_active ? 'aktif' : 'nonaktif' }}
                  </span>
                </td>
                <td v-if="canManage" class="px-4 py-3 text-right text-xs">
                  <button type="button" class="text-banten-gold hover:underline" @click="editPartner(p)">Edit</button>
                  <button
                    v-if="p.is_active"
                    type="button"
                    class="ml-3 text-banten-red hover:underline"
                    @click="deactivate(p)"
                  >
                    Nonaktifkan
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <PaginationBar :meta="partnersMeta" @update:page="onPartnersPage" />
      </div>

      <!-- Blast -->
      <div v-else-if="tab === 'blast'">
        <div v-if="!canManage" class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-12 text-center text-sm text-banten-navy/60">
          Hanya editor / admin media yang dapat mengirim blast.
        </div>
        <form v-else class="rounded-xl border border-banten-navy/10 bg-white/90 p-5" @submit.prevent="runBlast">
          <h2 class="font-display text-lg text-banten-navy">One-Click Media Blast</h2>
          <p class="mt-1 text-xs text-banten-navy/60">
            Kirim konten approved ke media mitra via WA Gateway + Email (demo mock).
          </p>

          <label class="mt-4 block text-sm font-medium text-banten-navy">Konten approved</label>
          <select
            v-model="blastForm.content_id"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          >
            <option v-if="!readyContent.length" value="" disabled>Tidak ada konten approved</option>
            <option v-for="c in readyContent" :key="c.id" :value="c.id">
              {{ c.title }} · {{ c.issue_title || `Isu #${c.issue_id}` }}
            </option>
          </select>

          <label class="mt-4 block text-sm font-medium text-banten-navy">Kanal</label>
          <div class="mt-2 flex flex-wrap gap-4 text-sm">
            <label class="flex items-center gap-2">
              <input v-model="blastForm.channel" type="radio" value="both" /> WA + Email
            </label>
            <label class="flex items-center gap-2">
              <input v-model="blastForm.channel" type="radio" value="whatsapp" /> WhatsApp saja
            </label>
            <label class="flex items-center gap-2">
              <input v-model="blastForm.channel" type="radio" value="email" /> Email saja
            </label>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <p class="text-sm font-medium text-banten-navy">Penerima</p>
            <button type="button" class="text-xs text-banten-gold hover:underline" @click="toggleSelectAll">
              {{ selectAll ? 'Kosongkan' : 'Pilih semua aktif' }}
            </button>
          </div>
          <div class="mt-2 max-h-56 space-y-2 overflow-y-auto rounded-md border border-banten-navy/10 p-3">
            <label
              v-for="p in partnersAll.filter((x) => x.is_active)"
              :key="p.id"
              class="flex items-center gap-3 text-sm"
            >
              <input
                type="checkbox"
                :checked="blastForm.partner_ids.includes(p.id)"
                @change="togglePartner(p.id)"
              />
              <span class="text-banten-navy">{{ p.name }}</span>
              <span class="text-xs text-banten-navy/50">{{ p.whatsapp }} · {{ p.email }}</span>
            </label>
          </div>

          <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
          <button
            type="submit"
            class="mt-5 rounded-md bg-banten-red px-5 py-2.5 text-sm font-medium text-white disabled:opacity-60"
            :disabled="blasting || !blastForm.content_id || !blastForm.partner_ids.length"
          >
            {{ blasting ? 'Mengirim...' : 'Blast Sekarang' }}
          </button>

          <div
            v-if="blastResult"
            class="mt-4 rounded-md border px-4 py-3 text-sm"
            :class="statusColor[blastResult.status]"
          >
            Blast #{{ blastResult.id }} · {{ blastResult.status }} ·
            terkirim {{ blastResult.result?.sent || 0 }}, gagal {{ blastResult.result?.failed || 0 }}
          </div>
        </form>
      </div>

      <!-- SLA -->
      <div v-else-if="tab === 'sla'">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <p class="text-sm text-banten-navy/65">
            Target SLA tayang: <strong>{{ slaMinutes }} menit</strong> setelah blast
          </p>
          <button
            v-if="canManage"
            type="button"
            class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
            @click="showSlaForm = !showSlaForm"
          >
            {{ showSlaForm ? 'Tutup' : '+ Catat SLA' }}
          </button>
        </div>

        <form
          v-if="showSlaForm && canManage"
          class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
          @submit.prevent="saveSla"
        >
          <h2 class="font-display text-lg text-banten-navy">Catat Kepatuhan SLA</h2>
          <div class="mt-4 grid gap-3 md:grid-cols-2">
            <div>
              <label class="text-sm font-medium text-banten-navy">Media mitra</label>
              <select v-model="slaForm.media_partner_id" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
                <option v-for="p in partnersAll" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Blast terkait (opsional)</label>
              <select v-model="slaForm.blast_log_id" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
                <option value="">— tanpa blast —</option>
                <option v-for="b in blasts" :key="b.id" :value="b.id">
                  Blast #{{ b.id }} · {{ b.sent_at }}
                </option>
              </select>
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Waktu tayang</label>
              <input v-model="slaForm.published_at" type="datetime-local" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Response (menit, opsional)</label>
              <input
                v-model="slaForm.response_minutes"
                type="number"
                min="0"
                placeholder="auto dari blast jika diisi"
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              />
            </div>
            <div class="md:col-span-2">
              <label class="flex items-center gap-2 text-sm text-banten-navy">
                <input v-model="slaForm.content_match" type="checkbox" />
                Isi pemberitaan sesuai rilis klarifikasi
              </label>
            </div>
            <div class="md:col-span-2">
              <label class="text-sm font-medium text-banten-navy">Catatan</label>
              <input v-model="slaForm.notes" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
            </div>
          </div>
          <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
          <button type="submit" class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan SLA' }}
          </button>
        </form>

        <div class="mb-6 overflow-x-auto rounded-xl border border-banten-navy/10 bg-white/80">
          <table class="min-w-full text-left text-sm">
            <thead class="border-b border-banten-navy/10 bg-banten-sand/50 text-xs uppercase text-banten-navy/60">
              <tr>
                <th class="px-4 py-3">Peringkat</th>
                <th class="px-4 py-3">Media</th>
                <th class="px-4 py-3">Compliance</th>
                <th class="px-4 py-3">Avg respon</th>
                <th class="px-4 py-3">Log</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, idx) in slaRanking" :key="r.partner_id" class="border-b border-banten-navy/5">
                <td class="px-4 py-3 font-semibold text-banten-navy">#{{ idx + 1 }}</td>
                <td class="px-4 py-3 text-banten-navy">{{ r.partner_name }}</td>
                <td class="px-4 py-3">
                  <span v-if="r.compliance_rate == null" class="text-banten-navy/45">—</span>
                  <span
                    v-else
                    class="rounded px-2 py-0.5 text-xs font-semibold"
                    :class="r.compliance_rate >= 80 ? 'bg-emerald-100 text-emerald-800' : r.compliance_rate >= 50 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'"
                  >
                    {{ r.compliance_rate }}%
                  </span>
                </td>
                <td class="px-4 py-3 text-banten-navy/70">
                  {{ r.avg_response_minutes != null ? `${r.avg_response_minutes} mnt` : '—' }}
                </td>
                <td class="px-4 py-3 text-banten-navy/70">{{ r.compliant }}/{{ r.total_logs }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 class="mb-3 font-display text-lg text-banten-navy">Histori SLA</h3>
        <div v-if="!slaLogs.length" class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-10 text-center text-sm text-banten-navy/60">
          Belum ada catatan SLA.
        </div>
        <div v-else class="space-y-2">
          <article
            v-for="s in slaLogs"
            :key="s.id"
            class="rounded-xl border border-banten-navy/10 bg-white/80 px-4 py-3 text-sm"
          >
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <span
                  class="rounded px-2 py-0.5 text-xs font-semibold"
                  :class="s.sla_compliant ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'"
                >
                  {{ s.sla_compliant ? 'compliant' : 'breach' }}
                </span>
                <span class="ml-2 font-medium text-banten-navy">{{ s.partner_name }}</span>
              </div>
              <span class="text-xs text-banten-navy/55">
                {{ s.response_minutes != null ? `${s.response_minutes} menit` : '—' }}
                · match: {{ s.content_match ? 'ya' : 'tidak' }}
              </span>
            </div>
            <p v-if="s.notes" class="mt-1 text-xs text-banten-navy/60">{{ s.notes }}</p>
          </article>
        </div>
        <PaginationBar :meta="slaMeta" @update:page="onSlaPage" />
      </div>

      <!-- Logs -->
      <div v-else>
        <div v-if="!blasts.length" class="rounded-xl border border-dashed border-banten-navy/20 px-6 py-12 text-center text-sm text-banten-navy/60">
          Belum ada riwayat blast.
        </div>
        <div v-else class="space-y-3">
          <article
            v-for="b in blasts"
            :key="b.id"
            class="rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4"
          >
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="statusColor[b.status]">
                    {{ b.status }}
                  </span>
                  <span class="text-xs text-banten-navy/50">{{ b.channel }}</span>
                </div>
                <p class="mt-2 font-display text-lg text-banten-navy">
                  Blast #{{ b.id }} · Konten #{{ b.content_id }}
                </p>
                <p class="mt-1 text-xs text-banten-navy/60">
                  {{ b.recipients?.length || 0 }} mitra ·
                  terkirim {{ b.result?.sent || 0 }} · gagal {{ b.result?.failed || 0 }} ·
                  {{ b.sent_at }}
                </p>
              </div>
            </div>
            <details v-if="b.result?.deliveries?.length" class="mt-3">
              <summary class="cursor-pointer text-xs text-banten-gold">Detail pengiriman</summary>
              <ul class="mt-2 max-h-40 space-y-1 overflow-y-auto text-xs text-banten-navy/70">
                <li v-for="(d, i) in b.result.deliveries" :key="i">
                  {{ d.partner_name }} · {{ d.channel }} → {{ d.to }} · {{ d.status }}
                </li>
              </ul>
            </details>
          </article>
        </div>
        <PaginationBar :meta="blastsMeta" @update:page="onBlastsPage" />
      </div>
    </template>
  </div>
</template>
