<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import RiskBadge from './RiskBadge.vue'
import { useProjectStore } from '../stores/project'

const router = useRouter()
const projectStore = useProjectStore()
const open = ref(false)
const alerts = ref([])
const unreadCount = ref(0)
const loading = ref(false)
const permission = ref(
  typeof Notification !== 'undefined' ? Notification.permission : 'denied',
)

let pollTimer = null
const seenIds = new Set()

const severityClass = {
  info: 'bg-sky-100 text-sky-800',
  high: 'bg-amber-100 text-amber-900',
  critical: 'bg-banten-red text-white',
}

const typeLabel = {
  content_ready: 'Siap konten',
  content_review: 'Perlu review',
  risk_threshold: 'Risiko',
  response_overdue: 'Terlambat',
  manual: 'Manual',
}

function alertHref(alert) {
  if (alert.href) return alert.href
  if (alert.issue_id) return `/issues/${alert.issue_id}`
  return ''
}

function formatAlertTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleString('id-ID', {
    timeZone: 'Asia/Jakarta',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

async function loadAlerts() {
  loading.value = true
  try {
    const { data } = await api.get('/alerts', { params: { per_page: 50 } })
    const items = data.data || []
    // Browser notification for newly arrived unread alerts
    for (const a of items) {
      if (!a.is_read && !seenIds.has(a.id)) {
        notifyBrowser(a)
        seenIds.add(a.id)
      }
    }
    for (const a of items) seenIds.add(a.id)
    alerts.value = items
    unreadCount.value = data.unread_count || 0
  } catch {
    // ignore poll errors (e.g. role without access)
  } finally {
    loading.value = false
  }
}

function notifyBrowser(alert) {
  if (typeof Notification === 'undefined') return
  if (Notification.permission !== 'granted') return
  try {
    const n = new Notification(alert.title, {
      body: alert.message,
      icon: '/pavicon.png',
      tag: `sb-alert-${alert.id}`,
    })
    n.onclick = () => {
      window.focus()
      const href = alertHref(alert)
      if (href) router.push(href)
      open.value = true
    }
  } catch {
    // ignore
  }
}

async function enableWebPush() {
  if (typeof Notification === 'undefined') return
  const result = await Notification.requestPermission()
  permission.value = result
}

async function markRead(alert) {
  const href = alertHref(alert)
  if (alert.is_read) {
    if (href) router.push(href)
    open.value = false
    return
  }
  await api.post(`/alerts/${alert.id}/read`)
  await loadAlerts()
  if (href) {
    router.push(href)
    open.value = false
  }
}

async function markAll() {
  await api.post('/alerts/read-all')
  await loadAlerts()
}

function onDocClick(e) {
  const root = e.target.closest?.('[data-alert-bell]')
  if (!root) open.value = false
}

onMounted(() => {
  loadAlerts()
  pollTimer = setInterval(loadAlerts, 20000)
  document.addEventListener('click', onDocClick)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  document.removeEventListener('click', onDocClick)
})

watch(open, (v) => {
  if (v) loadAlerts()
})

watch(
  () => projectStore.selectedId,
  () => {
    seenIds.clear()
    loadAlerts()
  },
)

const badge = computed(() => (unreadCount.value > 9 ? '9+' : String(unreadCount.value)))
</script>

<template>
  <div class="relative" data-alert-bell>
    <button
      type="button"
      class="relative rounded-lg border border-[#30363d] bg-[#161b22] px-2.5 py-1.5 text-[#c9d1d9] transition hover:border-emerald-500/40 hover:text-white"
      title="Alert Krisis"
      @click.stop="open = !open"
    >
      <span aria-hidden="true" class="block h-4 w-4">
        <svg viewBox="0 0 24 24" fill="none" class="h-4 w-4" stroke="currentColor" stroke-width="1.8">
          <path d="M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.2V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M9.5 17a2.5 2.5 0 0 0 5 0" stroke-linecap="round" />
        </svg>
      </span>
      <span
        v-if="unreadCount"
        class="absolute -right-1.5 -top-1.5 min-w-4 rounded-full bg-banten-red px-1 text-center text-[10px] font-bold leading-4 text-white"
      >
        {{ badge }}
      </span>
    </button>

    <div
      v-if="open"
      class="absolute right-0 z-40 mt-2 w-80 overflow-hidden rounded-xl border border-[#30363d] bg-[#161b22] text-[#c9d1d9] shadow-2xl sm:w-96"
      @click.stop
    >
      <div class="flex items-center justify-between border-b border-[#30363d] px-4 py-3">
        <div>
          <p class="text-sm font-semibold text-white">Alert Krisis</p>
          <p class="text-[11px] text-[#8b949e]">F.02 · Web + WA + Telegram</p>
        </div>
        <button
          v-if="unreadCount"
          type="button"
          class="text-[11px] text-emerald-400 hover:underline"
          @click="markAll"
        >
          Tandai semua dibaca
        </button>
      </div>

      <div
        v-if="permission === 'default'"
        class="border-b border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-200"
      >
        <button type="button" class="font-semibold underline" @click="enableWebPush">
          Aktifkan Web Notification
        </button>
      </div>

      <div class="max-h-80 overflow-y-auto">
        <p v-if="loading && !alerts.length" class="px-4 py-6 text-center text-xs text-[#8b949e]">
          Memuat...
        </p>
        <p v-else-if="!alerts.length" class="px-4 py-6 text-center text-xs text-[#8b949e]">
          Tidak ada alert.
        </p>
        <button
          v-for="a in alerts"
          :key="a.id"
          type="button"
          class="block w-full border-b border-[#30363d]/60 px-4 py-3 text-left transition hover:bg-[#21262d]"
          :class="!a.is_read ? 'bg-emerald-500/5' : ''"
          @click="markRead(a)"
        >
          <div class="flex items-center gap-2">
            <RiskBadge v-if="a.risk_level" :level="a.risk_level" />
            <span
              v-else
              class="rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase"
              :class="severityClass[a.severity] || severityClass.high"
              :title="a.severity"
            >
              {{ a.severity }}
            </span>
            <span v-if="!a.is_read" class="h-1.5 w-1.5 rounded-full bg-banten-red" />
          </div>
          <p class="mt-1 text-sm font-medium text-white line-clamp-1">{{ a.title }}</p>
          <p class="mt-0.5 text-xs text-[#8b949e] line-clamp-2">{{ a.message }}</p>
          <p class="mt-1 text-[10px] text-[#6e7681]">
            {{ typeLabel[a.alert_type] || a.alert_type }} · {{ formatAlertTime(a.created_at) }}
          </p>
        </button>
      </div>
    </div>
  </div>
</template>
