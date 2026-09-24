<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useValidationBadgeStore } from '../stores/validationBadge'
import RiskBadge from '../components/RiskBadge.vue'
import IssueStatusBadge from '../components/IssueStatusBadge.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import { ISSUE_STATUSES, issueStatusMeta } from '../config/issueStatus'

const route = useRoute()
const auth = useAuthStore()
const validationBadge = useValidationBadgeStore()

const issue = ref(null)
const loading = ref(true)
const error = ref('')
const masterOpds = ref([])
const opdAdmins = ref([])
const submitting = ref(false)
const closing = ref(false)
const statusError = ref('')
const formError = ref('')
const formNotice = ref('')
const form = ref({
  opd_id: '',
  assigned_to: '',
  request_notes: '',
})

const statusColor = {
  waiting: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
  validated: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  rejected: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
}

const inputClass =
  'mt-1 w-full rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#e6edf3] placeholder:text-[#6e7681] outline-none transition focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'

const FLOW_STEPS = ISSUE_STATUSES.map((code) => ({
  code,
  short: issueStatusMeta(code).short,
  description: issueStatusMeta(code).description,
  actor: issueStatusMeta(code).actor,
}))

const canRequest = computed(() => {
  const code = auth.user?.role?.code
  return code === 'super_admin' || code === 'editor'
})

const filteredAdmins = computed(() => {
  const opd = masterOpds.value.find((o) => String(o.id) === String(form.value.opd_id))
  if (!opd) return opdAdmins.value
  return opdAdmins.value.filter((a) => a.opd_name === opd.name)
})

const opdOptions = computed(() =>
  masterOpds.value.map((o) => ({ value: o.id, label: o.name })),
)

const adminOptions = computed(() =>
  filteredAdmins.value.map((a) => ({
    value: a.id,
    label: a.full_name || a.username || `Admin #${a.id}`,
  })),
)

const outletLabel = computed(() => issue.value?.source_label || null)

const actions = computed(() => {
  const list = issue.value?.recommended_actions
  return Array.isArray(list) ? list.filter(Boolean) : []
})

const metaChips = computed(() => {
  if (!issue.value) return []
  const chips = []
  if (outletLabel.value) chips.push({ label: outletLabel.value, tone: 'neutral' })
  if (issue.value.source === 'manual') chips.push({ label: 'Input manual', tone: 'emerald' })
  return chips
})

/** Severity 1–100 (100 = paling kritis/merah) */
const severityScore = computed(() => {
  const iss = issue.value
  if (!iss) return 0
  const assessment = iss.risk_assessment && typeof iss.risk_assessment === 'object'
    ? iss.risk_assessment
    : {}

  const ratio = Number(assessment.sentiment_negative_ratio)
  if (Number.isFinite(ratio) && ratio > 0) {
    return Math.min(100, Math.max(1, Math.round(ratio * 100)))
  }

  for (const key of ['sentiment_score', 'score', 'severity_score']) {
    const raw = Number(assessment[key])
    if (Number.isFinite(raw)) {
      return Math.min(100, Math.max(1, Math.round(Math.abs(raw))))
    }
  }

  const why = String(iss.why_now || '')
  const m = why.match(/score\s*(-?\d+(?:\.\d+)?)/i)
  if (m) {
    return Math.min(100, Math.max(1, Math.round(Math.abs(Number(m[1])))))
  }

  const riskMap = { R0: 10, R1: 25, R2: 45, R3: 65, R4: 80, R5: 95 }
  return riskMap[iss.risk_level] || 20
})

const severityMeta = computed(() => {
  const s = severityScore.value
  if (s >= 80) return { label: 'Kritis', bar: 'bg-rose-500', text: 'text-rose-400', track: 'bg-rose-500/15' }
  if (s >= 60) return { label: 'Tinggi', bar: 'bg-orange-500', text: 'text-orange-400', track: 'bg-orange-500/15' }
  if (s >= 40) return { label: 'Sedang', bar: 'bg-amber-400', text: 'text-amber-300', track: 'bg-amber-500/15' }
  if (s >= 20) return { label: 'Rendah', bar: 'bg-sky-400', text: 'text-sky-300', track: 'bg-sky-500/15' }
  return { label: 'Minimal', bar: 'bg-emerald-400', text: 'text-emerald-300', track: 'bg-emerald-500/15' }
})

const whyNowClean = computed(() => {
  const raw = String(issue.value?.why_now || '').trim()
  if (!raw) return ''
  // Hide auto-detect boilerplate that names SIPANTAU / Mata Bathin
  if (/deteksi otomatis|sipantau|mata\s*bathin/i.test(raw)) return ''
  return raw
})

const flowIndex = computed(() => {
  const idx = FLOW_STEPS.findIndex((s) => s.code === issue.value?.status)
  return idx >= 0 ? idx : 0
})

const flowSteps = computed(() =>
  FLOW_STEPS.map((step, i) => {
    let state = 'upcoming'
    if (i < flowIndex.value) state = 'done'
    else if (i === flowIndex.value) state = 'current'
    return { ...step, state, index: i }
  }),
)

watch(
  () => form.value.opd_id,
  () => {
    form.value.assigned_to = ''
  },
)

function formatDateTime(iso) {
  if (!iso) return '—'
  const hasZone = /[zZ]|[+-]\d{2}:\d{2}$/.test(iso)
  const d = new Date(hasZone ? iso : `${iso}Z`)
  if (Number.isNaN(d.getTime())) return '—'
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

function hostFromUrl(url) {
  if (!url) return null
  try {
    const host = new URL(url).hostname.replace(/^www\./, '')
    return host || null
  } catch {
    return null
  }
}

const GENERIC_SOURCE = new Set([
  'sipantau',
  'mata_bathin',
  'mata bathin',
  'manual',
  'media',
  'media online',
  'news',
  'evidence',
  'evidence pack',
  'evidence pack sipantau',
])

function evidenceLabel(e) {
  const host = hostFromUrl(e?.url)
  const name = (e?.source_name || '').trim()
  if (name && !GENERIC_SOURCE.has(name.toLowerCase())) return name
  if (host) return host
  const title = (e?.title || '').trim()
  if (title && !GENERIC_SOURCE.has(title.toLowerCase())) return title
  return 'Sumber berita'
}

function evidenceSubtitle(e) {
  const label = evidenceLabel(e)
  const title = (e?.title || '').trim()
  if (!title) return null
  if (GENERIC_SOURCE.has(title.toLowerCase())) return null
  if (title.toLowerCase() === label.toLowerCase()) return null
  return title
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/issues/${route.params.id}`)
    issue.value = data.data
    if (canRequest.value) {
      const [ops, admins] = await Promise.all([
        api.get('/opds', { params: { active: '1', per_page: 200 } }),
        api.get('/validations/opd-options'),
      ])
      masterOpds.value = ops.data.data || []
      opdAdmins.value = admins.data.data || []
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat detail isu'
  } finally {
    loading.value = false
  }
}

async function closeIssue() {
  if (!issue.value || issue.value.status === 'closed' || closing.value) return
  const current = issueStatusMeta(issue.value.status).short
  const ok = window.confirm(`Tutup isu ini? Status ${current} akan menjadi Closed.`)
  if (!ok) return
  closing.value = true
  statusError.value = ''
  try {
    const { data } = await api.patch(`/issues/${issue.value.id}/status`, { status: 'closed' })
    if (data?.data) {
      issue.value = { ...issue.value, ...data.data }
    }
  } catch (err) {
    statusError.value = err.response?.data?.error || 'Gagal menutup isu'
  } finally {
    closing.value = false
  }
}

async function requestValidation() {
  submitting.value = true
  formError.value = ''
  formNotice.value = ''
  try {
    const payload = {
      opd_id: Number(form.value.opd_id),
      request_notes: form.value.request_notes,
    }
    if (form.value.assigned_to) payload.assigned_to = Number(form.value.assigned_to)
    const { data } = await api.post(`/validations/issues/${route.params.id}`, payload)
    form.value.request_notes = ''
    form.value.assigned_to = ''
    formNotice.value = deliveryNotice(data.data?.delivery)
    validationBadge.refresh()
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal mengirim validasi'
  } finally {
    submitting.value = false
  }
}

function deliveryNotice(rows) {
  if (!Array.isArray(rows) || !rows.length) return 'Permintaan validasi terkirim.'
  const label = { whatsapp: 'WhatsApp', email: 'Email' }
  return rows
    .map((row) => {
      const name = label[row.channel] || row.channel
      if (row.status === 'sent') return `${name} terkirim`
      return `${name} tidak terkirim${row.error ? `: ${row.error}` : ''}`
    })
    .join(' · ')
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <RouterLink
      to="/crisis-room"
      class="inline-flex items-center gap-1.5 text-xs font-medium text-[#8b949e] transition hover:text-emerald-400"
    >
      <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
      </svg>
      Crisis Room
    </RouterLink>

    <div v-if="loading" class="space-y-3">
      <div class="h-28 animate-pulse rounded-2xl border border-[#30363d] bg-[#161b22]" />
      <div class="h-48 animate-pulse rounded-2xl border border-[#30363d] bg-[#161b22]" />
    </div>

    <div
      v-else-if="error"
      class="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300"
    >
      {{ error }}
    </div>

    <template v-else-if="issue">
      <!-- Header -->
      <section class="rounded-2xl border border-[#30363d] bg-[#161b22] px-5 py-5 sm:px-6">
        <div class="flex flex-wrap items-center gap-2">
          <RiskBadge :level="issue.risk_level" show-label tone="outline" />
          <IssueStatusBadge :status="issue.status" tone="outline" />
          <span
            v-for="chip in metaChips"
            :key="chip.label"
            class="inline-flex items-center rounded-md border px-2 py-0.5 text-[10px] font-semibold"
            :class="
              chip.tone === 'emerald'
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
                : 'border-[#30363d] bg-[#0d1117] text-[#c9d1d9]'
            "
          >
            {{ chip.label }}
          </span>
        </div>

        <h1 class="mt-3 text-2xl font-bold leading-snug tracking-tight text-white sm:text-3xl">
          {{ issue.title }}
        </h1>

        <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[11px] text-[#8b949e]">
          <span class="inline-flex items-center gap-1">
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l3.5 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            {{ formatDateTime(issue.created_at) }}
          </span>
          <span v-if="issue.updated_at && issue.updated_at !== issue.created_at">
            Update {{ formatDateTime(issue.updated_at) }}
          </span>
          <span v-if="issue.mb_alert_id" class="font-mono text-[#6e7681]">{{ issue.mb_alert_id }}</span>
        </div>
      </section>

      <!-- Flow tracker -->
      <section class="rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-4 sm:px-5">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p class="text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Alur penanganan</p>
            <p class="mt-1 text-[11px] text-[#8b949e]">
              Sekarang:
              <span class="font-semibold text-emerald-400">{{ issueStatusMeta(issue.status).short }}</span>
              <span v-if="issueStatusMeta(issue.status).actor" class="text-[#c9d1d9]">
                · {{ issueStatusMeta(issue.status).actor }}
              </span>
              <span v-if="issue.status === 'closed' && issue.closed_at" class="text-[#6e7681]">
                · {{ formatDateTime(issue.closed_at) }}
              </span>
            </p>
          </div>
          <button
            v-if="canRequest && issue.status !== 'closed'"
            type="button"
            class="rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-black transition hover:bg-emerald-400 disabled:opacity-60"
            :disabled="closing"
            @click="closeIssue"
          >
            {{ closing ? 'Menutup…' : 'Tutup isu' }}
          </button>
        </div>
        <p
          v-if="statusError"
          class="mb-3 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-300"
        >
          {{ statusError }}
        </p>
        <ol class="flex items-start gap-0 overflow-x-auto pb-1">
          <li
            v-for="(step, i) in flowSteps"
            :key="step.code"
            class="relative flex min-w-[5.25rem] flex-1 flex-col items-center text-center"
            :title="`${step.actor} — ${step.description}`"
          >
            <div
              v-if="i < flowSteps.length - 1"
              class="absolute left-1/2 top-3.5 h-0.5 w-full"
              :class="step.state === 'done' || step.state === 'current' ? 'bg-emerald-500/50' : 'bg-[#30363d]'"
              aria-hidden="true"
            />
            <span
              class="relative z-10 flex h-7 w-7 items-center justify-center rounded-full border text-[11px] font-bold"
              :class="{
                'border-emerald-500 bg-emerald-500 text-black': step.state === 'done',
                'border-emerald-400 bg-emerald-500/20 text-emerald-300 ring-2 ring-emerald-500/30': step.state === 'current',
                'border-[#30363d] bg-[#0d1117] text-[#6e7681]': step.state === 'upcoming',
              }"
            >
              <svg v-if="step.state === 'done'" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
              </svg>
              <span v-else>{{ i + 1 }}</span>
            </span>
            <span
              class="mt-2 text-[10px] font-semibold leading-tight"
              :class="step.state === 'upcoming' ? 'text-[#6e7681]' : 'text-[#e6edf3]'"
            >
              {{ step.short }}
            </span>
            <span
              class="mt-1.5 inline-flex rounded-full border px-1.5 py-0.5 text-[9px] font-semibold leading-none"
              :class="
                step.state === 'upcoming'
                  ? 'border-[#30363d] text-[#6e7681]'
                  : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
              "
            >
              {{ step.actor }}
            </span>
            <span class="mt-1 hidden max-w-[5.5rem] text-[9px] leading-tight text-[#6e7681] sm:block">
              {{ step.description }}
            </span>
          </li>
        </ol>
      </section>

      <div class="grid gap-4 lg:grid-cols-3">
        <section class="space-y-4 lg:col-span-2">
          <!-- Brief -->
          <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5 sm:p-6">
            <div class="flex items-center gap-2">
              <span class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#30363d] bg-[#0d1117] text-[#8b949e]">
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
              </span>
              <h2 class="text-sm font-semibold text-white">Issue brief</h2>
            </div>

            <p class="mt-4 text-sm leading-relaxed text-[#c9d1d9] whitespace-pre-wrap">
              {{ issue.summary || 'Belum ada ringkasan.' }}
            </p>

            <!-- Severity meter -->
            <div class="mt-4 rounded-xl border border-[#30363d] bg-[#0d1117]/70 px-4 py-3.5">
              <div class="flex flex-wrap items-end justify-between gap-2">
                <div>
                  <p class="text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">Tingkat urgensi</p>
                  <p class="mt-0.5 text-xs text-[#8b949e]">Skala 1–100 · semakin tinggi semakin kritis</p>
                </div>
                <div class="text-right">
                  <p class="text-2xl font-bold tabular-nums" :class="severityMeta.text">
                    {{ severityScore }}
                  </p>
                  <p class="text-[10px] font-semibold uppercase tracking-wider" :class="severityMeta.text">
                    {{ severityMeta.label }}
                  </p>
                </div>
              </div>
              <div class="mt-3 h-2.5 overflow-hidden rounded-full" :class="severityMeta.track">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="severityMeta.bar"
                  :style="{ width: `${severityScore}%` }"
                />
              </div>
              <div class="mt-1.5 flex justify-between text-[9px] font-medium text-[#6e7681]">
                <span>1 aman</span>
                <span>100 kritis</span>
              </div>
            </div>

            <div
              v-if="whyNowClean"
              class="mt-4 rounded-xl border border-amber-500/20 bg-amber-500/5 px-4 py-3"
            >
              <p class="text-[10px] font-bold uppercase tracking-wider text-amber-400/90">Why now</p>
              <p class="mt-1.5 text-sm leading-relaxed text-[#e6edf3]">{{ whyNowClean }}</p>
            </div>

            <div v-if="actions.length" class="mt-5">
              <p class="text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">
                Rekomendasi tindakan
              </p>
              <ul class="mt-2 space-y-2">
                <li
                  v-for="(a, i) in actions"
                  :key="i"
                  class="flex gap-2.5 rounded-lg border border-[#30363d] bg-[#0d1117]/70 px-3 py-2.5 text-sm text-[#c9d1d9]"
                >
                  <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-emerald-500/15 text-[10px] font-bold text-emerald-400">
                    {{ i + 1 }}
                  </span>
                  <span class="leading-relaxed">{{ a }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Evidence -->
          <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5 sm:p-6">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#30363d] bg-[#0d1117] text-[#8b949e]">
                  <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
                  </svg>
                </span>
                <h2 class="text-sm font-semibold text-white">Evidence pack</h2>
              </div>
              <span class="text-[11px] text-[#6e7681]">{{ issue.evidence?.length || 0 }} item</span>
            </div>

            <div
              v-if="!issue.evidence?.length"
              class="mt-4 rounded-xl border border-dashed border-[#30363d] px-4 py-8 text-center text-sm text-[#8b949e]"
            >
              Belum ada evidence terlampir.
            </div>

            <ul v-else class="mt-4 space-y-2.5">
              <li
                v-for="e in issue.evidence"
                :key="e.id"
                class="rounded-xl border border-[#30363d] bg-[#0d1117]/70 px-4 py-3 transition hover:border-emerald-500/30"
              >
                <div class="flex flex-wrap items-start justify-between gap-2">
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-[#e6edf3]">
                      {{ evidenceLabel(e) }}
                    </p>
                    <p v-if="evidenceSubtitle(e)" class="mt-0.5 text-xs text-[#8b949e]">
                      {{ evidenceSubtitle(e) }}
                    </p>
                  </div>
                  <a
                    v-if="e.url"
                    :href="e.url"
                    target="_blank"
                    rel="noopener"
                    class="inline-flex shrink-0 items-center gap-1 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-300 transition hover:bg-emerald-500/20"
                  >
                    Buka sumber
                    <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                    </svg>
                  </a>
                </div>
                <p v-if="e.url" class="mt-2 truncate font-mono text-[10px] text-[#6e7681]">{{ e.url }}</p>
                <p v-if="e.snippet" class="mt-2 text-xs leading-relaxed text-[#8b949e]">{{ e.snippet }}</p>
              </li>
            </ul>
          </div>
        </section>

        <!-- Side -->
        <section class="space-y-4">
          <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
            <div class="flex items-center gap-2">
              <span class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#30363d] bg-[#0d1117] text-[#8b949e]">
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
              </span>
              <div>
                <h2 class="text-sm font-semibold text-white">Validasi OPD</h2>
                <p class="text-[10px] text-[#6e7681]">Waiting → Validated → Rejected</p>
              </div>
            </div>

            <div v-if="issue.validations?.length" class="mt-4 space-y-2.5">
              <div
                v-for="v in issue.validations"
                :key="v.id"
                class="rounded-xl border border-[#30363d] bg-[#0d1117]/70 px-3.5 py-3"
              >
                <div class="flex items-center justify-between gap-2">
                  <p class="text-sm font-medium text-[#e6edf3]">{{ v.opd_name }}</p>
                  <span
                    class="rounded-md border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
                    :class="statusColor[v.status] || 'border-[#30363d] text-[#8b949e]'"
                  >
                    {{ v.status }}
                  </span>
                </div>
                <p v-if="v.request_notes" class="mt-1.5 text-xs text-[#8b949e]">{{ v.request_notes }}</p>
                <p v-if="v.response_notes" class="mt-2 text-xs text-[#c9d1d9]">
                  <span class="font-semibold text-emerald-400">Respon:</span> {{ v.response_notes }}
                </p>
              </div>
            </div>
            <p v-else class="mt-4 text-sm text-[#8b949e]">Belum ada permintaan validasi.</p>

            <form
              v-if="canRequest"
              class="mt-5 border-t border-[#30363d] pt-4"
              @submit.prevent="requestValidation"
            >
              <p class="text-xs font-semibold text-white">Kirim ke OPD</p>
              <label class="mt-3 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">OPD</label>
              <SearchableSelect
                v-model="form.opd_id"
                tone="dark"
                required
                :options="opdOptions"
                placeholder="— pilih OPD —"
                search-placeholder="Cari nama OPD…"
              />
              <label class="mt-3 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">
                OPD Admin (opsional)
              </label>
              <SearchableSelect
                v-model="form.assigned_to"
                tone="dark"
                :options="adminOptions"
                placeholder="— auto-assign bila ada —"
                search-placeholder="Cari admin…"
              />
              <label class="mt-3 block text-[10px] font-bold uppercase tracking-wider text-[#6e7681]">
                Catatan
              </label>
              <textarea
                v-model="form.request_notes"
                rows="3"
                :class="inputClass"
                placeholder="Mohon verifikasi data terkait isu ini…"
              />
              <p v-if="formNotice" class="mt-2 text-xs leading-relaxed text-emerald-300">{{ formNotice }}</p>
              <p v-if="formError" class="mt-2 text-sm text-rose-400">{{ formError }}</p>
              <button
                type="submit"
                class="mt-3 w-full rounded-xl bg-emerald-500 px-3 py-2.5 text-sm font-semibold text-black transition hover:bg-emerald-400 disabled:opacity-60"
                :disabled="submitting"
              >
                {{ submitting ? 'Mengirim…' : 'Kirim permintaan validasi' }}
              </button>
            </form>
          </div>

          <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#30363d] bg-[#0d1117] text-[#8b949e]">
                  <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125" />
                  </svg>
                </span>
                <div>
                  <h2 class="text-sm font-semibold text-white">Konten klarifikasi</h2>
                  <p class="text-[10px] text-[#6e7681]">Draft → Review → Approve</p>
                </div>
              </div>
              <RouterLink
                v-if="canRequest"
                :to="`/konten?issue_id=${issue.id}`"
                class="rounded-lg border border-emerald-500/40 bg-emerald-500/15 px-2.5 py-1 text-[11px] font-semibold text-emerald-300 transition hover:bg-emerald-500/25"
              >
                + Buat
              </RouterLink>
            </div>

            <div v-if="issue.content_items?.length" class="mt-4 space-y-2">
              <RouterLink
                v-for="c in issue.content_items"
                :key="c.id"
                :to="`/konten/${c.id}`"
                class="block rounded-xl border border-[#30363d] bg-[#0d1117]/70 px-3.5 py-2.5 transition hover:border-emerald-500/35"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="truncate text-sm font-medium text-[#e6edf3]">{{ c.title }}</span>
                  <span class="shrink-0 text-[10px] font-semibold uppercase tracking-wide text-[#8b949e]">
                    {{ c.status }}
                  </span>
                </div>
              </RouterLink>
            </div>
            <p v-else class="mt-4 text-sm text-[#8b949e]">Belum ada konten untuk isu ini.</p>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
