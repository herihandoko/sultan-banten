<script setup>
import { computed, onMounted, ref } from 'vue'
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
import api from '../services/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

const data = ref(null)
const loading = ref(true)
const error = ref('')

const brand = {
  navy: '#1B3A5C',
  gold: '#D4A017',
  red: '#C0392B',
  green: '#2E7D4F',
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/dashboard')
    data.value = res.data.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat dashboard'
  } finally {
    loading.value = false
  }
}

const kpis = computed(() => data.value?.kpis || {})

const trendChart = computed(() => {
  const t = data.value?.trend_7d
  if (!t) return null
  return {
    labels: t.labels,
    datasets: [
      {
        label: 'Positif',
        data: t.positif,
        borderColor: brand.green,
        backgroundColor: 'rgba(46, 125, 79, 0.08)',
        tension: 0.35,
        fill: false,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2.5,
      },
      {
        label: 'Negatif',
        data: t.negatif,
        borderColor: brand.red,
        backgroundColor: 'rgba(192, 57, 43, 0.08)',
        tension: 0.35,
        fill: false,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2.5,
      },
    ],
  }
})

const trendOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'bottom',
      labels: { boxWidth: 10, usePointStyle: true, pointStyle: 'circle', font: { size: 12 } },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: '#64748b', font: { size: 11 } },
    },
    y: {
      beginAtZero: true,
      suggestedMax: 80,
      grid: { color: 'rgba(27, 58, 92, 0.06)' },
      ticks: { color: '#94a3b8', font: { size: 11 } },
      border: { display: false },
    },
  },
}

const severityBar = {
  tinggi: 'bg-banten-red',
  sedang: 'bg-amber-400',
  rendah: 'bg-sky-400',
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

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Dashboard</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          Ringkasan situasi publik — intelijen Mata Bathin
        </p>
      </div>
      <div class="flex items-center gap-2">
        <span
          v-if="data?.source === 'mata_bathin_stub'"
          class="rounded-md bg-amber-50 px-2.5 py-1 text-[11px] font-medium text-amber-800 ring-1 ring-amber-200/80"
        >
          Data demo · stub Mata Bathin
        </span>
        <button
          type="button"
          class="rounded-md border border-banten-navy/20 px-3 py-1.5 text-xs text-banten-navy hover:bg-white"
          @click="load"
        >
          Refresh
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat dashboard...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <template v-else-if="data">
      <!-- KPI row -->
      <section class="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-2xl bg-white px-5 py-4 shadow-sm ring-1 ring-banten-navy/5">
          <p class="text-sm text-slate-500">Total mention</p>
          <p class="mt-2 font-display text-3xl tracking-tight text-slate-900">
            {{ formatMention(kpis.total_mention) }}
          </p>
        </div>
        <div class="rounded-2xl bg-white px-5 py-4 shadow-sm ring-1 ring-banten-navy/5">
          <p class="text-sm text-slate-500">Sentimen negatif</p>
          <p class="mt-2 font-display text-3xl tracking-tight text-banten-red">
            {{ kpis.sentiment_negative_pct }}%
          </p>
        </div>
        <div class="rounded-2xl bg-white px-5 py-4 shadow-sm ring-1 ring-banten-navy/5">
          <p class="text-sm text-slate-500">Reach</p>
          <p class="mt-2 font-display text-3xl tracking-tight text-slate-900">
            {{ formatReach(kpis.reach) }}
          </p>
        </div>
        <div class="rounded-2xl bg-white px-5 py-4 shadow-sm ring-1 ring-banten-navy/5">
          <p class="text-sm text-slate-500">Isu aktif</p>
          <p class="mt-2 font-display text-3xl tracking-tight text-slate-900">
            {{ kpis.active_issues }}
          </p>
        </div>
      </section>

      <!-- Trend + Alerts -->
      <section class="mb-5 grid gap-4 lg:grid-cols-[1.6fr_1fr]">
        <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-banten-navy/5">
          <h2 class="text-base font-semibold text-slate-800">
            Tren volume &amp; sentimen mention (7 hari)
          </h2>
          <div class="mt-4 h-64">
            <Line v-if="trendChart" :data="trendChart" :options="trendOptions" />
          </div>
        </div>

        <div class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-banten-navy/5">
          <div class="flex items-center justify-between gap-2">
            <h2 class="text-base font-semibold text-slate-800">Alert isu aktif</h2>
            <RouterLink to="/crisis-room" class="text-xs text-banten-gold hover:underline">
              Crisis Room →
            </RouterLink>
          </div>
          <ul class="mt-4 space-y-3">
            <li v-for="(alert, idx) in data.alerts" :key="alert.id || idx">
              <component
                :is="alert.id ? RouterLink : 'div'"
                :to="alert.id ? `/issues/${alert.id}` : undefined"
                class="flex gap-3 rounded-xl bg-slate-50/80 px-3 py-3 transition"
                :class="alert.id ? 'hover:bg-slate-100' : ''"
              >
                <span
                  class="mt-0.5 w-1 shrink-0 self-stretch rounded-full"
                  :class="severityBar[alert.severity] || 'bg-slate-300'"
                />
                <div class="min-w-0">
                  <p class="truncate font-medium text-slate-800">{{ alert.title }}</p>
                  <p class="mt-0.5 text-xs text-slate-500">
                    Severity {{ alert.severity }} · {{ alert.ago }}
                  </p>
                </div>
              </component>
            </li>
          </ul>
        </div>
      </section>

      <!-- Platforms -->
      <section class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-banten-navy/5">
        <h2 class="text-base font-semibold text-slate-800">Sebaran isu per platform</h2>
        <div class="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div
            v-for="p in data.platforms"
            :key="p.key"
            class="flex items-center gap-4 rounded-xl border border-slate-100 bg-slate-50/50 px-4 py-4"
          >
            <span
              class="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-white text-banten-navy shadow-sm ring-1 ring-slate-100"
            >
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
              <p class="text-sm text-slate-500">{{ p.label }}</p>
              <p class="font-display text-2xl text-slate-900">{{ formatMention(p.count) }}</p>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
