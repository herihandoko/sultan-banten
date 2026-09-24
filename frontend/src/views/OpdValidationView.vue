<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useValidationBadgeStore } from '../stores/validationBadge'
import RiskBadge from '../components/RiskBadge.vue'
import IssueStatusBadge from '../components/IssueStatusBadge.vue'

const auth = useAuthStore()
const validationBadge = useValidationBadgeStore()
const route = useRoute()
const items = ref([])
const meta = ref(null)
const page = ref(1)
const loading = ref(true)
const error = ref('')
const filters = ref({ q: '', status: 'waiting' })
const activeId = ref(null)
const responding = ref(false)
const responseForm = ref({
  status: 'validated',
  response_notes: '',
})
const formError = ref('')

const statusMeta = {
  waiting: {
    label: 'Menunggu',
    className: 'border border-amber-400/40 bg-amber-400/15 text-amber-300',
  },
  validated: {
    label: 'Tervalidasi',
    className: 'border border-emerald-500/40 bg-emerald-500/15 text-emerald-300',
  },
  rejected: {
    label: 'Ditolak',
    className: 'border border-rose-400/40 bg-rose-400/15 text-rose-300',
  },
}

const riskAccent = {
  R0: 'from-slate-500/80',
  R1: 'from-sky-500/80',
  R2: 'from-amber-400/80',
  R3: 'from-orange-500/80',
  R4: 'from-rose-500/80',
  R5: 'from-red-500',
}

const inputClass =
  'mt-1 w-full rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2.5 text-sm text-[#e6edf3] placeholder:text-[#6e7681] outline-none transition hover:border-[#484f58] focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'

const canRespond = computed(() => {
  const code = auth.user?.role?.code
  return code === 'super_admin' || code === 'opd_admin'
})

const active = computed(() => items.value.find((i) => i.id === activeId.value) || null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, per_page: 10 }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.q) params.q = filters.value.q
    const { data } = await api.get('/validations', { params })
    items.value = data.data || []
    meta.value = data.meta || null
    validationBadge.refresh()
    if (activeId.value && !items.value.find((i) => i.id === activeId.value)) {
      activeId.value = null
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat validasi OPD'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  load()
}

function resetFilters() {
  filters.value = { q: '', status: '' }
  page.value = 1
  load()
}

function onPage(p) {
  page.value = p
  load()
}

async function respond() {
  if (!active.value) return
  responding.value = true
  formError.value = ''
  try {
    await api.patch(`/validations/${active.value.id}/respond`, responseForm.value)
    responseForm.value = { status: 'validated', response_notes: '' }
    activeId.value = null
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal mengirim respon'
  } finally {
    responding.value = false
  }
}

function formatDateTime(iso) {
  if (!iso) return ''
  const hasZone = /[zZ]|[+-]\d{2}:\d{2}$/.test(iso)
  const when = new Date(hasZone ? iso : `${iso}Z`)
  if (Number.isNaN(when.getTime())) return ''
  const date = when.toLocaleDateString('id-ID', {
    timeZone: 'Asia/Jakarta',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
  const time = when.toLocaleTimeString('id-ID', {
    timeZone: 'Asia/Jakarta',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
  return `${date} · ${time} WIB`
}

function statusOf(item) {
  return statusMeta[item?.status] || {
    label: item?.status || '—',
    className: 'border border-slate-400/40 bg-slate-400/15 text-slate-300',
  }
}

function outletLabel(item) {
  const issue = item?.issue
  if (issue?.source_label) return issue.source_label
  const named = (issue?.evidence || []).find((row) => row.source_name)
  return named?.source_name || ''
}

function openRespond(item) {
  activeId.value = item.id
  responseForm.value = { status: 'validated', response_notes: '' }
  formError.value = ''
}

async function openFromLink() {
  const raw = Array.isArray(route.query.id) ? route.query.id[0] : route.query.id
  const id = Number(raw)
  if (!id) return
  try {
    const { data } = await api.get(`/validations/${id}`)
    const item = data.data
    if (!item) return
    if (!items.value.some((row) => row.id === item.id)) {
      items.value = [item, ...items.value]
    }
    if (item.status === 'waiting' && canRespond.value) openRespond(item)
  } catch {
    /* daftar tetap tampil bila tautan tidak berlaku */
  }
}

onMounted(async () => {
  await load()
  await openFromLink()
})
</script>

<template>
  <div class="space-y-6">
    <section class="rounded-xl border border-[#30363d] bg-[#161b22] px-4 py-3.5 sm:px-5">
      <div class="flex flex-wrap items-center gap-2.5">
        <span
          class="inline-flex items-center rounded-md border border-amber-400/40 bg-amber-400/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-amber-300"
        >
          F.03
        </span>
        <div class="min-w-0">
          <h1 class="text-lg font-bold tracking-tight text-white sm:text-xl">Validasi OPD</h1>
          <p class="text-[11px] text-[#6e7681]">
            Verifikasi data isu ke OPD teknis terkait
          </p>
        </div>
      </div>
    </section>

    <form
      class="overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22]"
      @submit.prevent="applyFilters"
    >
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#30363d]/80 px-4 py-3 sm:px-5">
        <div class="flex items-center gap-2">
          <span class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#30363d] bg-[#0d1117] text-[#8b949e]">
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 4.5h18M6 9.75h12M9 15h6M11 20.25h2" />
            </svg>
          </span>
          <div>
            <p class="text-sm font-semibold text-white">Filter permintaan</p>
            <p class="text-[11px] text-[#6e7681]">Cari judul isu, nama OPD, atau catatan</p>
          </div>
        </div>
        <button
          type="button"
          class="rounded-lg px-2.5 py-1.5 text-[11px] font-semibold text-[#8b949e] transition hover:bg-[#21262d] hover:text-white"
          @click="resetFilters"
        >
          Reset
        </button>
      </div>
      <div class="grid gap-3 px-4 py-4 sm:px-5 md:grid-cols-3">
        <div class="md:col-span-2">
          <label class="text-[11px] font-medium text-[#8b949e]">Kata kunci</label>
          <input
            v-model="filters.q"
            type="search"
            placeholder="Judul isu, nama OPD, catatan..."
            :class="inputClass"
          />
        </div>
        <div>
          <label class="text-[11px] font-medium text-[#8b949e]">Status</label>
          <select v-model="filters.status" :class="inputClass">
            <option value="">Semua</option>
            <option value="waiting">Menunggu</option>
            <option value="validated">Tervalidasi</option>
            <option value="rejected">Ditolak</option>
          </select>
        </div>
      </div>
      <div class="flex justify-end border-t border-[#30363d]/80 px-4 py-3 sm:px-5">
        <button
          type="submit"
          class="rounded-lg border border-emerald-500/40 bg-emerald-500/15 px-4 py-2 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-500/25"
        >
          Cari
        </button>
      </div>
    </form>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 3" :key="n" class="h-36 animate-pulse rounded-2xl border border-[#30363d] bg-[#161b22]" />
    </div>
    <div v-else-if="error" class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
      {{ error }}
    </div>
    <div
      v-else-if="!items.length"
      class="rounded-2xl border border-dashed border-[#30363d] bg-[#161b22] px-6 py-16 text-center"
    >
      <p class="text-lg font-semibold text-white">Tidak ada permintaan validasi</p>
      <p class="mx-auto mt-2 max-w-md text-sm text-[#8b949e]">
        Permintaan dari Crisis Room akan muncul di sini.
      </p>
    </div>
    <div v-else class="space-y-3">
      <article
        v-for="item in items"
        :key="item.id"
        class="relative overflow-hidden rounded-2xl border bg-[#161b22] transition duration-200"
        :class="activeId === item.id ? 'border-emerald-500/40' : 'border-[#30363d]'"
      >
        <div
          class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent"
          :class="riskAccent[item.issue?.risk_level] || 'from-slate-500/80'"
          aria-hidden="true"
        />
        <div class="px-5 py-4 pl-6">
          <div class="flex items-start justify-between gap-3">
            <h2 class="text-base font-semibold leading-snug text-white sm:text-lg">
              {{ item.issue?.title || `Isu #${item.issue_id}` }}
            </h2>
            <span
              class="shrink-0 inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold"
              :class="statusOf(item).className"
            >
              {{ statusOf(item).label }}
            </span>
          </div>

          <div class="mt-2 flex flex-wrap items-center gap-2">
            <RiskBadge v-if="item.issue?.risk_level" :level="item.issue.risk_level" show-label tone="outline" />
            <span class="inline-flex items-center rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]">
              {{ item.opd_name }}
            </span>
            <span
              v-if="outletLabel(item)"
              class="inline-flex items-center rounded-md border border-[#30363d] bg-[#0d1117] px-2 py-0.5 text-[10px] font-semibold text-[#c9d1d9]"
            >
              {{ outletLabel(item) }}
            </span>
            <IssueStatusBadge v-if="item.issue?.status" :status="item.issue.status" tone="outline" />
            <span
              v-if="item.requested_at"
              class="inline-flex items-center gap-1 text-[11px] text-[#6e7681]"
            >
              <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l3.5 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              Diminta {{ formatDateTime(item.requested_at) }}
            </span>
            <span
              v-if="item.issue?.evidence?.length"
              class="inline-flex items-center gap-1 text-[11px] text-[#8b949e]"
            >
              {{ item.issue.evidence.length }} berkas bukti
            </span>
          </div>

          <p class="mt-2 line-clamp-3 text-sm leading-relaxed text-[#c9d1d9]">
            {{ item.request_notes || 'Tanpa catatan permintaan' }}
          </p>
          <p
            v-if="item.issue?.summary && item.issue.summary !== item.request_notes"
            class="mt-1 line-clamp-2 text-sm leading-relaxed text-[#8b949e]"
          >
            {{ item.issue.summary }}
          </p>

          <p
            v-if="item.response_notes && item.status !== 'waiting'"
            class="mt-3 rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm leading-relaxed text-[#c9d1d9]"
          >
            <span class="text-[11px] font-semibold uppercase tracking-wide text-[#6e7681]">Respon OPD</span>
            <span v-if="item.responded_at" class="ml-2 text-[11px] text-[#6e7681]">{{ formatDateTime(item.responded_at) }}</span>
            <span class="mt-1 block">{{ item.response_notes }}</span>
          </p>
        </div>

        <div
          v-if="activeId === item.id"
          class="border-t border-[#30363d]/80 bg-[#0d1117]/50 px-5 py-4 pl-6"
        >
          <p class="text-sm font-semibold text-white">Hasil verifikasi</p>
          <div class="mt-3 flex flex-wrap gap-2 text-sm">
            <label
              class="inline-flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-1.5"
              :class="responseForm.status === 'validated' ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300' : 'border-[#30363d] text-[#c9d1d9]'"
            >
              <input v-model="responseForm.status" type="radio" value="validated" class="accent-emerald-400" />
              Tervalidasi
            </label>
            <label
              class="inline-flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-1.5"
              :class="responseForm.status === 'rejected' ? 'border-rose-400/40 bg-rose-400/15 text-rose-300' : 'border-[#30363d] text-[#c9d1d9]'"
            >
              <input v-model="responseForm.status" type="radio" value="rejected" class="accent-rose-400" />
              Ditolak
            </label>
          </div>
          <textarea
            v-model="responseForm.response_notes"
            rows="3"
            :class="inputClass"
            placeholder="Catatan hasil verifikasi..."
          />
          <p v-if="formError" class="mt-2 text-sm text-rose-300">{{ formError }}</p>
          <div class="mt-3 flex gap-2">
            <button
              type="button"
              class="rounded-lg border border-emerald-500/40 bg-emerald-500/15 px-3 py-1.5 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-500/25 disabled:opacity-60"
              :disabled="responding"
              @click="respond"
            >
              {{ responding ? 'Mengirim...' : 'Kirim respon' }}
            </button>
            <button
              type="button"
              class="rounded-lg border border-[#30363d] px-3 py-1.5 text-sm text-[#c9d1d9] transition hover:border-[#484f58] hover:text-white"
              @click="activeId = null"
            >
              Batal
            </button>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-[#30363d]/80 px-5 py-2.5 pl-6 text-[12px] font-medium">
          <RouterLink
            :to="`/issues/${item.issue_id}`"
            class="inline-flex items-center gap-1.5 text-sky-400 transition hover:text-emerald-400"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5M8.25 15.75 21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            Lihat isu
          </RouterLink>
          <button
            v-if="canRespond && item.status === 'waiting'"
            type="button"
            class="inline-flex items-center gap-1.5 text-sky-400 transition hover:text-emerald-400"
            @click="openRespond(item)"
          >
            <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v8.018Z" />
            </svg>
            Respon
          </button>
        </div>
      </article>
    </div>

    <div
      v-if="meta && meta.total > 0"
      class="flex flex-wrap items-center justify-between gap-3 border-t border-[#30363d] pt-4 text-sm"
    >
      <p class="text-[#8b949e]">
        Menampilkan
        <span class="font-medium text-[#e6edf3]">
          {{ (meta.page - 1) * meta.per_page + 1 }}–{{ Math.min(meta.page * meta.per_page, meta.total) }}
        </span>
        dari
        <span class="font-medium text-[#e6edf3]">{{ meta.total }}</span>
      </p>
      <div class="flex items-center gap-1.5">
        <button
          type="button"
          class="rounded-lg border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-[#c9d1d9] transition hover:border-[#484f58] hover:text-white disabled:opacity-40"
          :disabled="!meta.has_prev"
          @click="onPage(meta.page - 1)"
        >
          ‹ Prev
        </button>
        <span class="min-w-16 px-2 text-center tabular-nums text-[#8b949e]">
          {{ meta.page }} / {{ meta.pages || 1 }}
        </span>
        <button
          type="button"
          class="rounded-lg border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-[#c9d1d9] transition hover:border-[#484f58] hover:text-white disabled:opacity-40"
          :disabled="!meta.has_next"
          @click="onPage(meta.page + 1)"
        >
          Next ›
        </button>
      </div>
    </div>
  </div>
</template>
