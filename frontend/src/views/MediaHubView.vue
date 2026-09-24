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
const messagingStatus = ref(null)
const testEmailForm = ref({ to: '', subject: '[SIAGAPIM] Test email', body: '' })
const testWaForm = ref({ to: '', message: '' })
const testingEmail = ref(false)
const testingWa = ref(false)
const testEmailResult = ref(null)
const testWaResult = ref(null)
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

const activePartnerCount = computed(() => partnersAll.value.length)
const readyCount = computed(() => readyContent.value.length)
const blastTotal = computed(() => blastsMeta.value?.total || 0)
const slaAverage = computed(() => {
  const rows = slaRanking.value.filter((row) => row.compliance_rate != null)
  if (!rows.length) return null
  return Math.round(rows.reduce((sum, row) => sum + Number(row.compliance_rate), 0) / rows.length)
})

const BLAST_STATUS = {
  sent: { label: 'Terkirim', chip: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' },
  partial: { label: 'Sebagian', chip: 'border-amber-500/40 bg-amber-500/10 text-amber-300' },
  failed: { label: 'Gagal', chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300' },
  pending: { label: 'Menunggu', chip: 'border-slate-500/40 bg-slate-500/10 text-slate-300' },
}

const CHANNEL_LABEL = {
  both: 'WA + Email',
  whatsapp: 'WhatsApp',
  email: 'Email',
}

const inputClass =
  'mt-1 w-full rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2.5 text-sm text-[#e6edf3] placeholder:text-[#6e7681] outline-none transition focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'

function blastStatus(status) {
  return BLAST_STATUS[status] || { label: status, chip: 'border-[#30363d] text-[#c9d1d9]' }
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
      api.get('/media/messaging-status'),
    ]
    if (canManage.value) reqs.push(api.get('/media/blast-ready-content'))
    const [pRes, pAllRes, bRes, slaRes, rankRes, msgRes, cRes] = await Promise.all(reqs)
    partners.value = pRes.data.data || []
    partnersMeta.value = pRes.data.meta || null
    partnersAll.value = pAllRes.data.data || []
    blasts.value = bRes.data.data || []
    blastsMeta.value = bRes.data.meta || null
    slaLogs.value = slaRes.data.data || []
    slaMeta.value = slaRes.data.meta || null
    slaMinutes.value = slaRes.data.sla_minutes || 60
    slaRanking.value = rankRes.data.data || []
    messagingStatus.value = msgRes.data.data || null
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

async function runTestEmail() {
  testingEmail.value = true
  testEmailResult.value = null
  formError.value = ''
  try {
    const payload = {
      to: testEmailForm.value.to.trim(),
      subject: testEmailForm.value.subject || undefined,
    }
    if (testEmailForm.value.body.trim()) payload.body = testEmailForm.value.body.trim()
    const { data } = await api.post('/media/test-email', payload)
    testEmailResult.value = data.data
  } catch (err) {
    testEmailResult.value = err.response?.data?.data || {
      status: 'failed',
      error: err.response?.data?.error || 'Gagal kirim test email',
    }
  } finally {
    testingEmail.value = false
  }
}

async function runTestWhatsapp() {
  testingWa.value = true
  testWaResult.value = null
  formError.value = ''
  try {
    const payload = { to: testWaForm.value.to.trim() }
    if (testWaForm.value.message.trim()) payload.message = testWaForm.value.message.trim()
    const { data } = await api.post('/media/test-whatsapp', payload)
    testWaResult.value = data.data
  } catch (err) {
    testWaResult.value = err.response?.data?.data || {
      status: 'failed',
      error: err.response?.data?.error || 'Gagal kirim test WhatsApp',
    }
  } finally {
    testingWa.value = false
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
        <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-400/80">F.06 · F.07 · F.08</p>
        <h1 class="mt-1 font-display text-3xl text-white">Media Hub</h1>
        <p class="mt-1 max-w-xl text-sm text-[#8b949e]">
          Mitra media, blast klarifikasi, dan kepatuhan SLA tayang dalam satu ruang kerja.
        </p>
      </div>
      <div class="flex flex-wrap gap-1 rounded-xl border border-[#30363d] bg-[#161b22] p-1 text-xs">
        <button
          v-for="t in [
            { key: 'partners', label: 'Media Mitra' },
            { key: 'blast', label: 'Media Blast' },
            { key: 'sla', label: 'SLA' },
            { key: 'logs', label: 'Riwayat Blast' },
          ]"
          :key="t.key"
          type="button"
          class="rounded-lg px-3 py-1.5 font-semibold transition"
          :class="tab === t.key ? 'bg-emerald-500 text-black' : 'text-[#c9d1d9] hover:bg-[#21262d]'"
          @click="tab = t.key"
        >
          {{ t.label }}
        </button>
      </div>
    </div>

    <section class="mb-6 grid grid-cols-2 gap-2 lg:grid-cols-4">
      <button type="button" class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-3 text-left" @click="tab = 'partners'">
        <p class="text-[10px] font-semibold uppercase tracking-wider text-[#6e7681]">Mitra aktif</p>
        <p class="mt-1 text-2xl font-bold tabular-nums text-white">{{ activePartnerCount }}</p>
      </button>
      <button type="button" class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-3 text-left" @click="tab = 'blast'">
        <p class="text-[10px] font-semibold uppercase tracking-wider text-[#6e7681]">Siap di-blast</p>
        <p class="mt-1 text-2xl font-bold tabular-nums text-emerald-300">{{ readyCount }}</p>
      </button>
      <button type="button" class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-3 text-left" @click="tab = 'logs'">
        <p class="text-[10px] font-semibold uppercase tracking-wider text-[#6e7681]">Riwayat blast</p>
        <p class="mt-1 text-2xl font-bold tabular-nums text-white">{{ blastTotal }}</p>
      </button>
      <button type="button" class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-3 text-left" @click="tab = 'sla'">
        <p class="text-[10px] font-semibold uppercase tracking-wider text-[#6e7681]">Rata kepatuhan</p>
        <p class="mt-1 text-2xl font-bold tabular-nums text-amber-300">{{ slaAverage == null ? '—' : `${slaAverage}%` }}</p>
        <p class="text-[10px] text-[#6e7681]">Target tayang {{ slaMinutes }} menit</p>
      </button>
    </section>

    <form
      v-if="tab === 'partners' || tab === 'logs'"
      class="mb-6 rounded-2xl border border-[#30363d] bg-[#161b22] p-4"
      @submit.prevent="applyFilters"
    >
      <div class="grid gap-3 md:grid-cols-4 md:items-end">
        <div class="md:col-span-2">
          <label class="text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Kata kunci</label>
          <input
            v-model="filters.q"
            type="search"
            :placeholder="tab === 'partners' ? 'Nama media, editor, wilayah…' : 'Judul konten atau kanal…'"
            :class="inputClass"
          />
        </div>
        <div v-if="tab === 'partners'">
          <label class="text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Status mitra</label>
          <select v-model="filters.active" :class="inputClass">
            <option value="">Semua</option>
            <option value="1">Aktif</option>
            <option value="0">Nonaktif</option>
          </select>
        </div>
        <div v-if="tab === 'logs'">
          <label class="text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Status blast</label>
          <select v-model="filters.blast_status" :class="inputClass">
            <option value="">Semua</option>
            <option value="sent">Terkirim</option>
            <option value="partial">Sebagian</option>
            <option value="failed">Gagal</option>
            <option value="pending">Menunggu</option>
          </select>
        </div>
        <div class="flex flex-wrap gap-2">
          <button type="submit" class="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black hover:bg-emerald-400">Terapkan</button>
          <button type="button" class="rounded-xl border border-[#30363d] px-4 py-2.5 text-sm text-[#c9d1d9] hover:bg-[#21262d]" @click="resetFilters">
            Reset
          </button>
        </div>
      </div>
    </form>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 3" :key="n" class="h-28 animate-pulse rounded-2xl border border-[#30363d] bg-[#161b22]" />
    </div>
    <div v-else-if="error" class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
      {{ error }}
    </div>

    <template v-else>
      <!-- Partners -->
      <div v-if="tab === 'partners'">
        <div class="mb-4 flex justify-end">
          <button
            v-if="canManage"
            type="button"
            class="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black hover:bg-emerald-400"
            @click="showForm = !showForm; if (!showForm) resetPartnerForm()"
          >
            {{ showForm ? 'Tutup' : '+ Tambah Mitra' }}
          </button>
        </div>

        <form
          v-if="showForm && canManage"
          class="mb-6 rounded-2xl border border-emerald-500/25 bg-[#161b22] p-5"
          @submit.prevent="savePartner"
        >
          <h2 class="text-base font-semibold text-white">
            {{ editingId ? 'Edit Media Mitra' : 'Media Mitra Baru' }}
          </h2>
          <div class="mt-4 grid gap-3 md:grid-cols-2">
            <div>
              <label class="text-[11px] font-medium text-[#8b949e]">Nama media</label>
              <input v-model="partnerForm.name" required :class="inputClass" />
            </div>
            <div>
              <label class="text-[11px] font-medium text-[#8b949e]">Pemred / kontak</label>
              <input v-model="partnerForm.editor_name" :class="inputClass" />
            </div>
            <div>
              <label class="text-[11px] font-medium text-[#8b949e]">WhatsApp</label>
              <input v-model="partnerForm.whatsapp" placeholder="62812…" :class="inputClass" />
            </div>
            <div>
              <label class="text-[11px] font-medium text-[#8b949e]">Email</label>
              <input v-model="partnerForm.email" type="email" :class="inputClass" />
            </div>
            <div>
              <label class="text-[11px] font-medium text-[#8b949e]">Wilayah coverage</label>
              <input v-model="partnerForm.coverage_area" :class="inputClass" />
            </div>
            <div>
              <label class="text-[11px] font-medium text-[#8b949e]">Kanal darurat krisis</label>
              <input v-model="partnerForm.crisis_channel" :class="inputClass" />
            </div>
          </div>
          <p v-if="formError" class="mt-3 text-sm text-rose-400">{{ formError }}</p>
          <button type="submit" class="mt-4 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-60" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </form>

        <div v-if="!partners.length" class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22]/60 px-6 py-12 text-center text-sm text-[#8b949e]">
          Belum ada media mitra.
        </div>
        <div v-else class="space-y-3">
          <article
            v-for="p in partners"
            :key="p.id"
            class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
          >
            <div
              class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent"
              :class="p.is_active ? 'from-emerald-500/80' : 'from-slate-500/80'"
              aria-hidden="true"
            />
            <div class="px-5 py-4 pl-6">
              <div class="flex items-start justify-between gap-3">
                <h2 class="text-base font-semibold text-white">{{ p.name }}</h2>
                <span
                  class="shrink-0 inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold"
                  :class="p.is_active ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-slate-500/40 bg-slate-500/10 text-slate-300'"
                >
                  {{ p.is_active ? 'Aktif' : 'Nonaktif' }}
                </span>
              </div>
              <p class="mt-1 text-sm text-[#8b949e]">{{ p.editor_name || 'Kontak belum diisi' }}</p>
              <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">WA {{ p.whatsapp || '—' }}</span>
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ p.email || 'Email —' }}</span>
                <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-1 text-[#c9d1d9]">{{ p.coverage_area || 'Wilayah —' }}</span>
                <span v-if="p.crisis_channel" class="rounded-md border border-amber-500/30 bg-amber-500/10 px-2 py-1 text-amber-200">
                  Krisis: {{ p.crisis_channel }}
                </span>
              </div>
            </div>
            <div v-if="canManage" class="flex gap-4 border-t border-[#30363d]/80 px-5 py-2.5 pl-6 text-xs font-semibold">
              <button type="button" class="text-emerald-300 hover:text-emerald-200" @click="editPartner(p)">Edit</button>
              <button v-if="p.is_active" type="button" class="text-rose-300 hover:text-rose-200" @click="deactivate(p)">
                Nonaktifkan
              </button>
            </div>
          </article>
        </div>
        <PaginationBar :meta="partnersMeta" @update:page="onPartnersPage" />
      </div>

      <!-- Blast -->
      <div v-else-if="tab === 'blast'">
        <div v-if="!canManage" class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22]/60 px-6 py-12 text-center text-sm text-[#8b949e]">
          Hanya editor / admin media yang dapat mengirim blast.
        </div>
        <div v-else class="space-y-5">
          <div v-if="messagingStatus" class="flex flex-wrap gap-2">
            <span
              class="inline-flex items-center rounded-lg border px-3 py-1.5 text-xs font-semibold"
              :class="messagingStatus.whatsapp?.enabled ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-amber-500/40 bg-amber-500/10 text-amber-200'"
            >
              WhatsApp {{ messagingStatus.whatsapp?.enabled ? 'aktif' : 'belum ada token' }}
            </span>
            <span
              class="inline-flex items-center rounded-lg border px-3 py-1.5 text-xs font-semibold"
              :class="messagingStatus.mail?.enabled ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-amber-500/40 bg-amber-500/10 text-amber-200'"
            >
              Email {{ messagingStatus.mail?.enabled ? `aktif · ${messagingStatus.mail.host}` : 'nonaktif' }}
            </span>
          </div>

          <form class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5" @submit.prevent="runBlast">
          <h2 class="text-base font-semibold text-white">One-Click Media Blast</h2>
          <p class="mt-1 text-xs text-[#8b949e]">
            Kirim konten yang sudah disetujui ke mitra lewat WhatsApp dan email.
          </p>

          <label class="mt-4 block text-[11px] font-medium text-[#8b949e]">Konten approved</label>
          <select v-model="blastForm.content_id" required :class="inputClass">
            <option v-if="!readyContent.length" value="" disabled>Tidak ada konten approved</option>
            <option v-for="c in readyContent" :key="c.id" :value="c.id">
              {{ c.title }} · {{ c.issue_title || `Isu #${c.issue_id}` }}
            </option>
          </select>

          <p class="mt-4 text-[11px] font-medium text-[#8b949e]">Kanal</p>
          <div class="mt-2 flex flex-wrap gap-2 text-sm">
            <label
              v-for="opt in [
                { value: 'both', label: 'WA + Email' },
                { value: 'whatsapp', label: 'WhatsApp saja' },
                { value: 'email', label: 'Email saja' },
              ]"
              :key="opt.value"
              class="inline-flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2"
              :class="blastForm.channel === opt.value ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' : 'border-[#30363d] text-[#c9d1d9]'"
            >
              <input v-model="blastForm.channel" type="radio" :value="opt.value" class="accent-emerald-500" />
              {{ opt.label }}
            </label>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <p class="text-sm font-medium text-white">
              Penerima
              <span class="ml-1 text-xs font-normal text-[#6e7681]">{{ blastForm.partner_ids.length }} dipilih</span>
            </p>
            <button type="button" class="text-xs font-semibold text-emerald-300 hover:text-emerald-200" @click="toggleSelectAll">
              {{ selectAll ? 'Kosongkan' : 'Pilih semua aktif' }}
            </button>
          </div>
          <div class="mt-2 max-h-56 space-y-2 overflow-y-auto rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
            <label
              v-for="p in partnersAll.filter((x) => x.is_active)"
              :key="p.id"
              class="flex items-center gap-3 rounded-lg px-2 py-1.5 text-sm hover:bg-[#161b22]"
            >
              <input
                type="checkbox"
                class="accent-emerald-500"
                :checked="blastForm.partner_ids.includes(p.id)"
                @change="togglePartner(p.id)"
              />
              <span class="text-[#e6edf3]">{{ p.name }}</span>
              <span class="text-xs text-[#6e7681]">{{ p.whatsapp || '—' }} · {{ p.email || '—' }}</span>
            </label>
          </div>

          <p v-if="formError" class="mt-3 text-sm text-rose-400">{{ formError }}</p>
          <button
            type="submit"
            class="mt-5 rounded-lg bg-rose-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-rose-400 disabled:opacity-60"
            :disabled="blasting || !blastForm.content_id || !blastForm.partner_ids.length"
          >
            {{ blasting ? 'Mengirim...' : 'Blast Sekarang' }}
          </button>

          <div
            v-if="blastResult"
            class="mt-4 rounded-xl border px-4 py-3 text-sm"
            :class="blastStatus(blastResult.status).chip"
          >
            Blast #{{ blastResult.id }} · {{ blastStatus(blastResult.status).label }} ·
            terkirim {{ blastResult.result?.sent || 0 }}, gagal {{ blastResult.result?.failed || 0 }}
          </div>
          </form>

          <div class="grid gap-5 md:grid-cols-2">
            <form class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5" @submit.prevent="runTestEmail">
              <h3 class="font-display text-base text-banten-navy">Uji kirim email</h3>
              <p class="mt-1 text-xs text-banten-navy/60">Kirim satu email uji lewat SMTP Media Hub.</p>
              <label class="mt-3 block text-xs font-medium text-banten-navy/70">Ke</label>
              <input
                v-model="testEmailForm.to"
                type="email"
                required
                placeholder="nama@domain.go.id"
                :class="inputClass"
              />
              <label class="mt-3 block text-xs font-medium text-banten-navy/70">Subjek</label>
              <input
                v-model="testEmailForm.subject"
                type="text"
                :class="inputClass"
              />
              <button
                type="submit"
                class="mt-4 rounded-md border border-banten-navy/20 bg-banten-sand/60 px-4 py-2 text-sm font-medium text-banten-navy disabled:opacity-60"
                :disabled="testingEmail || !testEmailForm.to"
              >
                {{ testingEmail ? 'Mengirim...' : 'Kirim test email' }}
              </button>
              <p
                v-if="testEmailResult"
                class="mt-3 text-xs"
                :class="testEmailResult.status === 'sent' ? 'text-emerald-700' : 'text-banten-red'"
              >
                {{ testEmailResult.status }}
                <template v-if="testEmailResult.error"> — {{ testEmailResult.error }}</template>
                <template v-else-if="testEmailResult.preview"> — {{ testEmailResult.preview }}</template>
              </p>
            </form>

            <form class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5" @submit.prevent="runTestWhatsapp">
              <h3 class="font-display text-base text-banten-navy">Uji kirim WhatsApp</h3>
              <p class="mt-1 text-xs text-banten-navy/60">
                Via
                <a
                  href="https://docs.fonnte.com/api-send-message/"
                  target="_blank"
                  rel="noopener"
                  class="text-banten-gold underline"
                >Fonnte</a>
              </p>
              <label class="mt-3 block text-xs font-medium text-banten-navy/70">Nomor</label>
              <input
                v-model="testWaForm.to"
                type="text"
                required
                placeholder="0812… atau 62812…"
                :class="inputClass"
              />
              <label class="mt-3 block text-xs font-medium text-banten-navy/70">Pesan (opsional)</label>
              <textarea
                v-model="testWaForm.message"
                rows="2"
                :class="inputClass"
                placeholder="Kosongkan untuk pesan uji default"
              />
              <button
                type="submit"
                class="mt-4 rounded-md border border-banten-navy/20 bg-banten-sand/60 px-4 py-2 text-sm font-medium text-banten-navy disabled:opacity-60"
                :disabled="testingWa || !testWaForm.to"
              >
                {{ testingWa ? 'Mengirim...' : 'Kirim test WA' }}
              </button>
              <p
                v-if="testWaResult"
                class="mt-3 text-xs"
                :class="testWaResult.status === 'sent' ? 'text-emerald-700' : 'text-banten-red'"
              >
                {{ testWaResult.status }}
                <template v-if="testWaResult.error"> — {{ testWaResult.error }}</template>
                <template v-else-if="testWaResult.message_id"> — id {{ testWaResult.message_id }}</template>
              </p>
            </form>
          </div>
        </div>
      </div>

      <!-- SLA -->
      <div v-else-if="tab === 'sla'">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <p class="text-sm text-[#8b949e]">
            Target tayang <strong class="text-white">{{ slaMinutes }} menit</strong> setelah blast.
          </p>
          <button
            v-if="canManage"
            type="button"
            class="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black hover:bg-emerald-400"
            @click="showSlaForm = !showSlaForm"
          >
            {{ showSlaForm ? 'Tutup' : '+ Catat SLA' }}
          </button>
        </div>

        <form
          v-if="showSlaForm && canManage"
          class="mb-6 rounded-2xl border border-[#30363d] bg-[#161b22] p-5"
          @submit.prevent="saveSla"
        >
          <h2 class="font-display text-lg text-banten-navy">Catat Kepatuhan SLA</h2>
          <div class="mt-4 grid gap-3 md:grid-cols-2">
            <div>
              <label class="text-sm font-medium text-banten-navy">Media mitra</label>
              <select v-model="slaForm.media_partner_id" required :class="inputClass">
                <option v-for="p in partnersAll" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Blast terkait (opsional)</label>
              <select v-model="slaForm.blast_log_id" :class="inputClass">
                <option value="">— tanpa blast —</option>
                <option v-for="b in blasts" :key="b.id" :value="b.id">
                  Blast #{{ b.id }} · {{ b.sent_at }}
                </option>
              </select>
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Waktu tayang</label>
              <input v-model="slaForm.published_at" type="datetime-local" :class="inputClass" />
            </div>
            <div>
              <label class="text-sm font-medium text-banten-navy">Response (menit, opsional)</label>
              <input
                v-model="slaForm.response_minutes"
                type="number"
                min="0"
                placeholder="auto dari blast jika diisi"
                :class="inputClass"
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
              <input v-model="slaForm.notes" :class="inputClass" />
            </div>
          </div>
          <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
          <button type="submit" class="mt-4 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-60" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan SLA' }}
          </button>
        </form>

        <div v-if="!slaRanking.length" class="mb-6 rounded-2xl border border-dashed border-[#30363d] px-6 py-10 text-center text-sm text-[#8b949e]">
          Belum ada peringkat mitra.
        </div>
        <div v-else class="mb-6 grid gap-3 sm:grid-cols-2">
          <article
            v-for="(r, idx) in slaRanking"
            :key="r.partner_id"
            class="rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-3"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-[11px] font-semibold text-[#6e7681]">#{{ idx + 1 }}</p>
                <h3 class="text-sm font-semibold text-white">{{ r.partner_name }}</h3>
              </div>
              <span
                v-if="r.compliance_rate != null"
                class="rounded-md border px-2 py-0.5 text-xs font-semibold"
                :class="r.compliance_rate >= 80 ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : r.compliance_rate >= 50 ? 'border-amber-500/40 bg-amber-500/10 text-amber-300' : 'border-rose-500/40 bg-rose-500/10 text-rose-300'"
              >
                {{ r.compliance_rate }}%
              </span>
              <span v-else class="text-xs text-[#6e7681]">Belum ada log</span>
            </div>
            <div class="mt-3 h-1.5 overflow-hidden rounded-full bg-[#30363d]">
              <div
                class="h-full rounded-full bg-emerald-400"
                :style="{ width: `${Math.min(100, r.compliance_rate || 0)}%` }"
              />
            </div>
            <p class="mt-2 text-[11px] text-[#8b949e]">
              Rata respon {{ r.avg_response_minutes != null ? `${r.avg_response_minutes} mnt` : '—' }}
              · patuh {{ r.compliant }}/{{ r.total_logs }}
            </p>
          </article>
        </div>

        <h3 class="mb-3 text-base font-semibold text-white">Histori SLA</h3>
        <div v-if="!slaLogs.length" class="rounded-2xl border border-dashed border-[#30363d] px-6 py-10 text-center text-sm text-[#8b949e]">
          Belum ada catatan SLA.
        </div>
        <div v-else class="space-y-2">
          <article
            v-for="s in slaLogs"
            :key="s.id"
            class="rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-3 text-sm"
          >
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span
                  class="rounded-md border px-2 py-0.5 text-[11px] font-semibold"
                  :class="s.sla_compliant ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-rose-500/40 bg-rose-500/10 text-rose-300'"
                >
                  {{ s.sla_compliant ? 'Patuh' : 'Lewat SLA' }}
                </span>
                <span class="font-medium text-white">{{ s.partner_name }}</span>
              </div>
              <span class="text-xs text-[#8b949e]">
                {{ s.response_minutes != null ? `${s.response_minutes} menit` : '—' }}
                · isi sesuai {{ s.content_match ? 'ya' : 'tidak' }}
              </span>
            </div>
            <p v-if="s.notes" class="mt-2 text-xs text-[#c9d1d9]">{{ s.notes }}</p>
          </article>
        </div>
        <PaginationBar :meta="slaMeta" @update:page="onSlaPage" />
      </div>

      <!-- Logs -->
      <div v-else>
        <div v-if="!blasts.length" class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22]/60 px-6 py-12 text-center text-sm text-[#8b949e]">
          Belum ada riwayat blast.
        </div>
        <div v-else class="space-y-3">
          <article
            v-for="b in blasts"
            :key="b.id"
            class="rounded-2xl border border-[#30363d] bg-[#161b22] px-5 py-4"
          >
            <div class="flex flex-wrap items-center gap-2">
              <span class="inline-flex rounded-md border px-2 py-0.5 text-[11px] font-semibold" :class="blastStatus(b.status).chip">
                {{ blastStatus(b.status).label }}
              </span>
              <span class="rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[11px] text-[#c9d1d9]">
                {{ CHANNEL_LABEL[b.channel] || b.channel }}
              </span>
            </div>
            <p class="mt-2 text-base font-semibold text-white">
              Blast #{{ b.id }}
            </p>
            <p class="mt-1 text-sm text-[#8b949e]">
              {{ b.recipients?.length || 0 }} mitra · terkirim {{ b.result?.sent || 0 }} · gagal {{ b.result?.failed || 0 }}
            </p>
            <p class="mt-1 text-[11px] text-[#6e7681]">{{ formatDateTime(b.sent_at) }}</p>
            <details v-if="b.result?.deliveries?.length" class="mt-3">
              <summary class="cursor-pointer text-xs font-semibold text-emerald-300">Detail pengiriman</summary>
              <ul class="mt-2 max-h-40 space-y-1 overflow-y-auto text-xs text-[#c9d1d9]">
                <li v-for="(d, i) in b.result.deliveries" :key="i">
                  {{ d.partner_name }} · {{ CHANNEL_LABEL[d.channel] || d.channel }} → {{ d.to }} · {{ blastStatus(d.status).label }}
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
