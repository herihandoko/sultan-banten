<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { Line } from 'vue-chartjs'
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import PageLoader from '../components/PageLoader.vue'
import api from '../services/api'
import { usePeriodStore } from '../stores/period'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

const periodStore = usePeriodStore()
const data = ref(null)
const loading = ref(true)
const reveal = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  reveal.value = false
  error.value = ''
  try {
    const res = await api.get('/dashboard', { params: { days: periodStore.days } })
    data.value = res.data.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat dashboard'
  } finally {
    loading.value = false
  }
}

const kpis = computed(() => data.value?.kpis || {})
const home = computed(() => data.value?.home || null)
const isMonitor = computed(() => home.value?.layout === 'monitor')

const trendChart = computed(() => {
  const t = data.value?.trend_7d
  if (!t) return null
  return {
    labels: t.labels,
    datasets: [
      {
        label: 'Positif',
        data: t.positif,
        borderColor: '#34d399',
        backgroundColor: 'rgba(52, 211, 153, 0.12)',
        tension: 0.35,
        fill: false,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2.5,
      },
      {
        label: 'Negatif',
        data: t.negatif,
        borderColor: '#fb7185',
        backgroundColor: 'rgba(251, 113, 133, 0.12)',
        tension: 0.35,
        fill: false,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2.5,
      },
    ],
  }
})

const trendOptions = computed(() => {
  const trend = data.value?.trend_7d
  const values = [...(trend?.positif || []), ...(trend?.negatif || [])]
  const max = values.length ? Math.max(...values) : 0
  return {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'bottom',
      labels: { boxWidth: 10, usePointStyle: true, pointStyle: 'circle', color: '#c9d1d9', font: { size: 12 } },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#8b949e', font: { size: 11 }, maxTicksLimit: 8, autoSkip: true },
    },
    y: {
      beginAtZero: true,
      ...(max === 0 ? { suggestedMax: 4 } : {}),
      grid: { color: 'rgba(48, 54, 61, 0.9)' },
      ticks: { color: '#8b949e', font: { size: 11 }, precision: 0 },
      border: { display: false },
    },
  },
}
})

const SEVERITY = {
  tinggi: { label: 'Tinggi', accent: 'from-rose-500/90', chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300' },
  sedang: { label: 'Sedang', accent: 'from-amber-400/90', chip: 'border-amber-500/40 bg-amber-500/10 text-amber-300' },
  rendah: { label: 'Rendah', accent: 'from-sky-400/90', chip: 'border-sky-500/40 bg-sky-500/10 text-sky-300' },
}

function severityOf(level) {
  return SEVERITY[level] || { label: level || '—', accent: 'from-slate-400/80', chip: 'border-[#30363d] text-[#c9d1d9]' }
}

function formatMention(n) {
  return new Intl.NumberFormat('id-ID').format(n || 0)
}

function formatReach(n) {
  if (!n) return '0'
  if (n >= 1_000_000) {
    const jt = n / 1_000_000
    return `${jt.toLocaleString('id-ID', { maximumFractionDigits: 1 })}jt`
  }
  if (n >= 1_000) return `${Math.round(n / 1000)}rb`
  return formatMention(n)
}

watch(
  () => periodStore.days,
  () => {
    load()
  },
)

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300/80">
          {{ home?.eyebrow || 'Beranda' }}
        </p>
        <h1 class="mt-1 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
          {{ home?.title || 'Dashboard SIAGAPIM' }}
        </h1>
        <p class="mt-1 text-sm text-[#8b949e]">
          {{ home?.subtitle || 'Pantauan mention, sentimen, dan isu aktif' }}
        </p>
      </div>
      <div class="flex items-center gap-2">
        <span
          v-if="data?.source === 'sipantau_stub'"
          class="rounded-md border border-amber-500/40 bg-amber-500/10 px-2.5 py-1 text-[11px] font-semibold text-amber-300"
        >
          SIPANTAU offline
        </span>
        <span
          v-else-if="data?.source === 'sipantau'"
          class="rounded-md border border-emerald-500/40 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-300"
        >
          Live · SIPANTAU
        </span>
        <span
          v-else-if="data?.source === 'mata_bathin_stub'"
          class="rounded-md border border-amber-500/40 bg-amber-500/10 px-2.5 py-1 text-[11px] font-semibold text-amber-300"
        >
          Data demo
        </span>
        <button
          type="button"
          class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-xs font-semibold text-[#c9d1d9] hover:border-emerald-500/40 hover:text-white"
          @click="load"
        >
          Muat ulang
        </button>
      </div>
    </div>

    <PageLoader v-if="!reveal" title="Memuat dashboard" :done="!loading" @finished="reveal = true" />
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <template v-else-if="data">
      <template v-if="isMonitor">
      <section class="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <article class="rounded-2xl border border-[#30363d] bg-[#161b22] px-5 py-4">
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Total mention</p>
          <p class="mt-2 text-3xl font-semibold tracking-tight text-white">{{ formatMention(kpis.total_mention) }}</p>
          <p class="mt-1 text-xs text-[#6e7681]">Percakapan yang tertangkap</p>
        </article>
        <article class="rounded-2xl border border-[#30363d] bg-[#161b22] px-5 py-4">
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Sentimen negatif</p>
          <p class="mt-2 text-3xl font-semibold tracking-tight text-rose-300">{{ kpis.sentiment_negative_pct }}%</p>
          <p class="mt-1 text-xs text-[#6e7681]">Porsi pembicaraan yang kurang baik</p>
        </article>
        <article class="rounded-2xl border border-[#30363d] bg-[#161b22] px-5 py-4">
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Jangkauan</p>
          <p class="mt-2 text-3xl font-semibold tracking-tight text-white">{{ formatReach(kpis.reach) }}</p>
          <p class="mt-1 text-xs text-[#6e7681]">Perkiraan orang yang terpapar</p>
        </article>
        <article class="rounded-2xl border border-[#30363d] bg-[#161b22] px-5 py-4">
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Isu aktif</p>
          <p class="mt-2 text-3xl font-semibold tracking-tight text-white">{{ kpis.active_issues }}</p>
          <p class="mt-1 text-xs text-[#6e7681]">Masih terbuka pada {{ periodStore.label.toLowerCase() }}</p>
        </article>
      </section>

      <section class="mb-4 grid items-stretch gap-4 lg:grid-cols-5">
        <div class="min-w-0 rounded-2xl border border-[#30363d] bg-[#161b22] p-5 lg:col-span-3">
          <h2 class="text-base font-semibold text-white">Tren mention · {{ periodStore.label }}</h2>
          <p class="mt-1 text-xs text-[#8b949e]">Garis hijau untuk sentimen positif, garis merah untuk negatif.</p>
          <div class="mt-4 h-64">
            <Line v-if="trendChart" :data="trendChart" :options="trendOptions" />
          </div>
        </div>

        <div class="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] p-5 lg:col-span-2">
          <div class="flex shrink-0 items-center justify-between gap-2">
            <div>
              <h2 class="text-base font-semibold text-white">Isu yang perlu perhatian</h2>
              <p class="mt-1 text-xs text-[#8b949e]">Enam isu aktif pada {{ periodStore.label.toLowerCase() }}</p>
            </div>
            <RouterLink to="/crisis-room" class="shrink-0 text-xs font-semibold text-emerald-300 hover:text-emerald-200">
              Crisis Room
            </RouterLink>
          </div>
          <ul class="mt-4 max-h-64 min-h-0 flex-1 space-y-2 overflow-y-auto">
            <li v-for="(alert, idx) in data.alerts" :key="alert.id || idx" class="min-w-0">
              <component
                :is="alert.id ? RouterLink : 'div'"
                :to="alert.id ? `/issues/${alert.id}` : undefined"
                class="relative flex min-w-0 gap-3 overflow-hidden rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-3 pl-4 transition"
                :class="alert.id ? 'hover:border-emerald-500/35' : ''"
              >
                <span class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b to-transparent" :class="severityOf(alert.severity).accent" />
                <div class="min-w-0 flex-1 overflow-hidden">
                  <p class="line-clamp-2 text-sm font-semibold leading-snug text-white">{{ alert.title }}</p>
                  <div class="mt-2 flex flex-wrap items-center gap-2">
                    <span class="rounded-md border px-2 py-0.5 text-[10px] font-semibold" :class="severityOf(alert.severity).chip">
                      {{ severityOf(alert.severity).label }}
                    </span>
                    <span v-if="alert.risk_level" class="text-[11px] text-[#8b949e]">{{ alert.risk_level }}</span>
                    <span class="text-[11px] text-[#6e7681]">{{ alert.ago }}</span>
                  </div>
                </div>
              </component>
            </li>
            <li v-if="!(data.alerts || []).length" class="rounded-xl border border-dashed border-[#30363d] px-4 py-8 text-center text-sm text-[#8b949e]">
              Tidak ada isu aktif pada periode ini.
            </li>
          </ul>
        </div>
      </section>

      <section v-if="home" class="mb-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
        <h2 class="text-base font-semibold text-white">{{ home.tasks_title }}</h2>
        <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div
            v-for="card in home.cards"
            :key="card.label"
            class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3"
          >
            <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">{{ card.label }}</p>
            <p class="mt-1 text-2xl font-semibold text-white">{{ card.value }}</p>
            <p class="mt-1 text-xs text-[#6e7681]">{{ card.hint }}</p>
          </div>
        </div>
        <ul v-if="home.tasks?.length" class="mt-4 space-y-2">
          <li v-for="(task, idx) in home.tasks" :key="idx">
            <RouterLink
              :to="task.href"
              class="flex items-center justify-between gap-4 rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 transition hover:border-emerald-500/35"
            >
              <span class="min-w-0 text-sm font-semibold leading-snug text-white">{{ task.title }}</span>
              <span class="shrink-0 text-right text-[11px] text-[#8b949e]">{{ task.meta }}</span>
            </RouterLink>
          </li>
        </ul>
        <p v-else class="mt-4 text-sm text-[#8b949e]">{{ home.tasks_empty }}</p>
      </section>

      <section class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
        <h2 class="text-base font-semibold text-white">Sebaran per kanal</h2>
        <p class="mt-1 text-xs text-[#8b949e]">Jumlah mention pada {{ periodStore.label.toLowerCase() }}.</p>
        <div class="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div
            v-for="p in data.platforms"
            :key="p.key"
            class="flex items-center gap-4 rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-4"
          >
            <span class="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-[#30363d] bg-[#161b22] text-[#c9d1d9]">
              <!-- twitter/X -->
              <svg v-if="p.key === 'twitter'" class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.727-8.835L1.254 2.25H8.08l4.253 5.622L18.244 2.25Zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77Z" />
              </svg>
              <!-- news -->
              <svg v-else-if="p.key === 'news'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 5h12a2 2 0 0 1 2 2v12H6a2 2 0 0 1-2-2V5Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M18 9h2a1 1 0 0 1 1 1v7a2 2 0 0 1-2 2h-1M8 9h6M8 13h6M8 17h3" />
              </svg>
              <!-- instagram -->
              <svg v-else-if="p.key === 'instagram'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <rect x="3" y="3" width="18" height="18" rx="5" />
                <circle cx="12" cy="12" r="4" />
                <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
              </svg>
              <!-- whatsapp -->
              <svg v-else-if="p.key === 'whatsapp'" class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347Z" />
                <path d="M12.05 2.003A9.938 9.938 0 0 0 2.11 11.94c0 1.753.458 3.466 1.331 4.978L2 22l5.214-1.366A9.93 9.93 0 0 0 12.05 21.88 9.94 9.94 0 0 0 22 11.94 9.94 9.94 0 0 0 12.05 2.003Zm0 18.15a8.21 8.21 0 0 1-4.187-1.147l-.3-.178-3.094.812.826-3.017-.196-.31a8.2 8.2 0 0 1-1.26-4.38 8.27 8.27 0 0 1 8.31-8.25 8.27 8.27 0 0 1 8.25 8.31 8.27 8.27 0 0 1-8.25 8.25Z" />
              </svg>
            </span>
            <div>
              <p class="text-sm text-[#8b949e]">{{ p.label }}</p>
              <p class="text-2xl font-semibold text-white">{{ formatMention(p.count) }}</p>
            </div>
          </div>
        </div>
      </section>
      </template>

      <section v-else-if="home" class="space-y-4">
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="card in home.cards"
            :key="card.label"
            class="rounded-2xl border border-[#30363d] bg-[#161b22] px-5 py-4"
          >
            <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">{{ card.label }}</p>
            <p class="mt-2 text-3xl font-semibold tracking-tight text-white">{{ card.value }}</p>
            <p class="mt-1 text-xs text-[#6e7681]">{{ card.hint }}</p>
          </article>
        </div>
        <div class="grid gap-4" :class="home.links?.length ? 'lg:grid-cols-[minmax(0,1fr)_16rem]' : ''">
          <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
            <h2 class="text-base font-semibold text-white">{{ home.tasks_title }}</h2>
            <ul v-if="home.tasks?.length" class="mt-3 space-y-2">
              <li v-for="(task, idx) in home.tasks" :key="idx">
                <RouterLink
                  :to="task.href"
                  class="flex items-start justify-between gap-3 rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 transition hover:border-emerald-500/35"
                >
                  <span class="text-sm font-semibold leading-snug text-white">{{ task.title }}</span>
                  <span class="shrink-0 text-[11px] text-[#8b949e]">{{ task.meta }}</span>
                </RouterLink>
              </li>
            </ul>
            <p v-else class="mt-3 text-sm text-[#8b949e]">{{ home.tasks_empty }}</p>
          </div>
          <div v-if="home.links?.length" class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
            <h2 class="text-base font-semibold text-white">Lanjut ke</h2>
            <div class="mt-3 flex flex-col gap-2">
              <RouterLink
                v-for="link in home.links"
                :key="link.href"
                :to="link.href"
                class="rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 text-sm font-semibold text-emerald-300 transition hover:border-emerald-500/35"
              >
                {{ link.label }}
              </RouterLink>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
