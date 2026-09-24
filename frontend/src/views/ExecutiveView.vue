<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import PageLoader from '../components/PageLoader.vue'
import api from '../services/api'
import RiskBadge from '../components/RiskBadge.vue'
import RiskLegend from '../components/RiskLegend.vue'
import IssueStatusBadge from '../components/IssueStatusBadge.vue'
import { riskMeta, riskOptionLabel } from '../config/risk'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const data = ref(null)
const loading = ref(true)
const reveal = ref(false)
const error = ref('')

const brand = {
  navy: '#1B3A5C',
  gold: '#D4A017',
  red: '#C0392B',
  sand: '#E8EEF4',
}

async function load() {
  loading.value = true
  reveal.value = false
  error.value = ''
  try {
    const res = await api.get('/executive/dashboard')
    data.value = res.data.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat dashboard eksekutif'
  } finally {
    loading.value = false
  }
}

const kpis = computed(() => data.value?.kpis || {})

const riskChart = computed(() => {
  const rows = data.value?.risk_distribution || []
  return {
    labels: rows.map((r) => r.level),
    datasets: [
      {
        label: 'Jumlah isu',
        data: rows.map((r) => r.count),
        backgroundColor: rows.map((r) => riskMeta(r.level).chartColor),
      },
    ],
  }
})

const riskChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title(items) {
          const level = items[0]?.label
          return level ? riskOptionLabel(level) : ''
        },
        afterTitle(items) {
          const level = items[0]?.label
          return level ? riskMeta(level).description : ''
        },
      },
    },
  },
  scales: {
    x: {
      ticks: {
        color: '#8b949e',
        callback(value) {
          return this.getLabelForValue(value)
        },
        font: { size: 11 },
      },
      grid: { display: false },
    },
    y: {
      beginAtZero: true,
      ticks: { precision: 0, color: '#8b949e', font: { size: 11 } },
      grid: { color: 'rgba(48, 54, 61, 0.9)' },
      border: { display: false },
    },
  },
}

const CONTENT_STATUS = {
  draft: 'Draf',
  in_review: 'Review',
  approved: 'Disetujui',
  rejected: 'Ditolak',
  published: 'Terbit',
}

function contentStatusLabel(status) {
  return CONTENT_STATUS[status] || status
}

const asnChart = computed(() => {
  const rows = data.value?.asn_by_opd || []
  return {
    labels: rows.map((r) => r.opd_name),
    datasets: [
      {
        label: 'Partisipasi',
        data: rows.map((r) => r.total),
        backgroundColor: '#38bdf8',
      },
    ],
  }
})

const contentChart = computed(() => {
  const rows = data.value?.content_pipeline || []
  const colors = {
    draft: '#94a3b8',
    in_review: '#fbbf24',
    approved: '#34d399',
    rejected: brand.red,
    published: '#38bdf8',
  }
  return {
    labels: rows.map((r) => contentStatusLabel(r.status)),
    datasets: [
      {
        data: rows.map((r) => r.count),
        backgroundColor: rows.map((r) => colors[r.status] || brand.gold),
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { display: false } },
    y: {
      beginAtZero: true,
      ticks: { precision: 0, color: '#8b949e', font: { size: 11 } },
      grid: { color: 'rgba(48, 54, 61, 0.9)' },
      border: { display: false },
    },
  },
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 10, color: '#c9d1d9', font: { size: 11 } } },
  },
}

function formatNum(n) {
  return new Intl.NumberFormat('id-ID').format(n || 0)
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300/80">F.14</p>
        <h1 class="mt-1 text-2xl font-semibold tracking-tight text-white sm:text-3xl">Dashboard Eksekutif</h1>
        <p class="mt-1 text-sm text-[#8b949e]">Ringkasan krisis, validasi, ASN, dan KOL untuk pimpinan</p>
      </div>
      <button
        type="button"
        class="rounded-xl border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-xs font-semibold text-[#c9d1d9] hover:border-emerald-500/40 hover:text-white"
        @click="load"
      >
        Muat ulang
      </button>
    </div>

    <PageLoader v-if="!reveal" title="Memuat ringkasan" :done="!loading" @finished="reveal = true" />
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <template v-else-if="data">
      <!-- Executive brief -->
      <section class="relative mb-6 overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
        <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-amber-400/90 to-transparent" />
        <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-amber-300">Ringkasan untuk pimpinan</p>
        <h2 class="mt-2 text-xl font-semibold leading-snug text-white sm:text-2xl">
          {{ data.executive_brief.headline }}
        </h2>
        <p class="mt-2 max-w-3xl text-sm leading-relaxed text-[#c9d1d9]">{{ data.executive_brief.summary }}</p>
        <ul class="mt-4 space-y-2">
          <li
            v-for="(rec, i) in data.executive_brief.recommendations"
            :key="i"
            class="rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#c9d1d9]"
          >
            {{ i + 1 }}. {{ rec }}
          </li>
        </ul>
      </section>

      <section class="mb-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <article class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-4">
          <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-rose-400/90 to-transparent" />
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Isu aktif</p>
          <p class="mt-2 text-3xl font-semibold text-white">{{ kpis.active_issues }}</p>
          <p class="mt-1 text-xs text-rose-300">{{ kpis.critical_issues }} berisiko R3 ke atas</p>
        </article>
        <article class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-4">
          <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-amber-400/90 to-transparent" />
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Validasi OPD</p>
          <p class="mt-2 text-3xl font-semibold text-white">{{ kpis.waiting_validations }}</p>
          <p class="mt-1 text-xs text-[#6e7681]">Menunggu jawaban</p>
        </article>
        <article class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-4">
          <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-sky-400/90 to-transparent" />
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Blast 7 hari</p>
          <p class="mt-2 text-3xl font-semibold text-white">{{ kpis.blasts_7d }}</p>
          <p class="mt-1 text-xs text-[#6e7681]">{{ formatNum(kpis.blast_deliveries_7d) }} pengiriman</p>
        </article>
        <article class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-4">
          <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-emerald-400/90 to-transparent" />
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Partisipasi ASN</p>
          <p class="mt-2 text-3xl font-semibold text-white">{{ formatNum(kpis.asn_participations) }}</p>
          <p class="mt-1 text-xs text-[#6e7681]">{{ kpis.active_missions }} misi berjalan</p>
        </article>
        <article class="relative overflow-hidden rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-4">
          <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-violet-400/90 to-transparent" />
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">Jangkauan KOL</p>
          <p class="mt-2 text-3xl font-semibold text-white">{{ formatNum(kpis.kol_views) }}</p>
          <p class="mt-1 text-xs text-[#6e7681]">{{ kpis.kol_campaigns }} kampanye</p>
        </article>
      </section>

      <!-- Charts -->
      <section class="mb-6 grid gap-4 lg:grid-cols-3">
        <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-4 lg:col-span-1">
          <h3 class="text-base font-semibold text-white">Distribusi risiko</h3>
          <p class="mt-1 text-xs text-[#8b949e]">Jumlah isu menurut tingkat R0–R5.</p>
          <div class="mt-3 h-48">
            <Bar :data="riskChart" :options="riskChartOptions" />
          </div>
          <div class="mt-3 border-t border-[#30363d] pt-3">
            <p class="mb-2 text-[10px] font-semibold uppercase tracking-wide text-[#6e7681]">
              Keterangan R0–R5
            </p>
            <RiskLegend compact />
          </div>
        </div>
        <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-4 lg:col-span-1">
          <h3 class="text-base font-semibold text-white">Pipeline konten</h3>
          <p class="mt-1 text-xs text-[#8b949e]">Posisi naskah dari draf sampai terbit.</p>
          <div class="mt-3 h-56">
            <Doughnut v-if="contentChart.labels.length" :data="contentChart" :options="doughnutOptions" />
            <p v-else class="pt-16 text-center text-sm text-[#8b949e]">Belum ada konten</p>
          </div>
        </div>
        <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-4 lg:col-span-1">
          <h3 class="text-base font-semibold text-white">ASN per OPD</h3>
          <p class="mt-1 text-xs text-[#8b949e]">Partisipasi aparatur menurut perangkat daerah.</p>
          <div class="mt-3 h-56">
            <Bar v-if="asnChart.labels.length" :data="asnChart" :options="chartOptions" />
            <p v-else class="pt-16 text-center text-sm text-[#8b949e]">Belum ada partisipasi</p>
          </div>
        </div>
      </section>

      <!-- Critical issues -->
      <section class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h3 class="text-base font-semibold text-white">Isu prioritas</h3>
            <p class="mt-1 text-xs text-[#8b949e]">Isu aktif pada tingkat R3 ke atas.</p>
          </div>
          <RouterLink to="/crisis-room" class="text-xs font-semibold text-emerald-300 hover:text-emerald-200">Crisis Room</RouterLink>
        </div>
        <div v-if="!data.critical_issues?.length" class="mt-4 rounded-xl border border-dashed border-[#30363d] px-4 py-8 text-center text-sm text-[#8b949e]">
          Tidak ada isu kritis yang masih ditangani.
        </div>
        <ul v-else class="mt-4 space-y-2">
          <li v-for="issue in data.critical_issues" :key="issue.id">
            <RouterLink
              :to="`/issues/${issue.id}`"
              class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#30363d] bg-[#0d1117] px-4 py-3 transition hover:border-emerald-500/35"
            >
              <div class="min-w-0">
                <p class="text-sm font-semibold leading-snug text-white">{{ issue.title }}</p>
                <div class="mt-2">
                  <RiskBadge :level="issue.risk_level" show-label tone="outline" />
                </div>
              </div>
              <IssueStatusBadge :status="issue.status" tone="outline" />
            </RouterLink>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
