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
import api from '../services/api'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const data = ref(null)
const loading = ref(true)
const error = ref('')

const brand = {
  navy: '#1B3A5C',
  gold: '#D4A017',
  red: '#C0392B',
  sand: '#E8EEF4',
}

async function load() {
  loading.value = true
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
        backgroundColor: ['#94a3b8', '#38bdf8', '#fbbf24', '#fb923c', '#f87171', brand.red],
      },
    ],
  }
})

const asnChart = computed(() => {
  const rows = data.value?.asn_by_opd || []
  return {
    labels: rows.map((r) => r.opd_name),
    datasets: [
      {
        label: 'Partisipasi',
        data: rows.map((r) => r.total),
        backgroundColor: brand.navy,
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
    labels: rows.map((r) => r.status),
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
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } },
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
        <h1 class="font-display text-3xl text-banten-navy">Dashboard Eksekutif</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          F.14 — Ringkasan krisis, diseminasi, ASN & KOL untuk pimpinan
        </p>
      </div>
      <button
        type="button"
        class="rounded-md border border-banten-navy/20 px-3 py-1.5 text-xs text-banten-navy hover:bg-white"
        @click="load"
      >
        Refresh
      </button>
    </div>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat ringkasan...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <template v-else-if="data">
      <!-- Executive brief -->
      <section class="mb-6 rounded-xl border border-banten-gold/40 bg-gradient-to-br from-white to-amber-50/60 p-5">
        <p class="text-xs font-semibold tracking-wide text-banten-gold uppercase">Executive Brief</p>
        <h2 class="mt-2 font-display text-2xl text-banten-navy">
          {{ data.executive_brief.headline }}
        </h2>
        <p class="mt-2 text-sm text-banten-navy/75">{{ data.executive_brief.summary }}</p>
        <ul class="mt-3 list-disc space-y-1 pl-5 text-sm text-banten-navy/70">
          <li v-for="(rec, i) in data.executive_brief.recommendations" :key="i">{{ rec }}</li>
        </ul>
      </section>

      <!-- KPIs -->
      <section class="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 px-4 py-4">
          <p class="text-xs text-banten-navy/55">Isu aktif</p>
          <p class="mt-1 font-display text-3xl text-banten-navy">{{ kpis.active_issues }}</p>
          <p class="text-xs text-banten-red">{{ kpis.critical_issues }} kritis (R3+)</p>
        </div>
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 px-4 py-4">
          <p class="text-xs text-banten-navy/55">Validasi OPD</p>
          <p class="mt-1 font-display text-3xl text-banten-navy">{{ kpis.waiting_validations }}</p>
          <p class="text-xs text-banten-navy/50">menunggu respon</p>
        </div>
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 px-4 py-4">
          <p class="text-xs text-banten-navy/55">Blast 7 hari</p>
          <p class="mt-1 font-display text-3xl text-banten-navy">{{ kpis.blasts_7d }}</p>
          <p class="text-xs text-banten-navy/50">{{ formatNum(kpis.blast_deliveries_7d) }} delivery</p>
        </div>
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 px-4 py-4">
          <p class="text-xs text-banten-navy/55">Partisipasi ASN</p>
          <p class="mt-1 font-display text-3xl text-banten-navy">{{ formatNum(kpis.asn_participations) }}</p>
          <p class="text-xs text-banten-navy/50">{{ kpis.active_missions }} misi aktif</p>
        </div>
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 px-4 py-4">
          <p class="text-xs text-banten-navy/55">Reach KOL</p>
          <p class="mt-1 font-display text-3xl text-banten-navy">{{ formatNum(kpis.kol_views) }}</p>
          <p class="text-xs text-banten-navy/50">{{ kpis.kol_campaigns }} campaign</p>
        </div>
      </section>

      <!-- Charts -->
      <section class="mb-6 grid gap-4 lg:grid-cols-3">
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-4 lg:col-span-1">
          <h3 class="font-display text-lg text-banten-navy">Distribusi Risiko</h3>
          <div class="mt-3 h-56">
            <Bar :data="riskChart" :options="chartOptions" />
          </div>
        </div>
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-4 lg:col-span-1">
          <h3 class="font-display text-lg text-banten-navy">Pipeline Konten</h3>
          <div class="mt-3 h-56">
            <Doughnut v-if="contentChart.labels.length" :data="contentChart" :options="doughnutOptions" />
            <p v-else class="pt-16 text-center text-sm text-banten-navy/50">Belum ada konten</p>
          </div>
        </div>
        <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-4 lg:col-span-1">
          <h3 class="font-display text-lg text-banten-navy">ASN per OPD</h3>
          <div class="mt-3 h-56">
            <Bar v-if="asnChart.labels.length" :data="asnChart" :options="chartOptions" />
            <p v-else class="pt-16 text-center text-sm text-banten-navy/50">Belum ada partisipasi</p>
          </div>
        </div>
      </section>

      <!-- Critical issues -->
      <section class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
        <div class="flex items-center justify-between gap-3">
          <h3 class="font-display text-lg text-banten-navy">Isu Prioritas (R3+)</h3>
          <RouterLink to="/crisis-room" class="text-xs text-banten-gold hover:underline">Crisis Room →</RouterLink>
        </div>
        <div v-if="!data.critical_issues?.length" class="mt-4 text-sm text-banten-navy/60">
          Tidak ada isu kritis aktif.
        </div>
        <ul v-else class="mt-4 space-y-2">
          <li
            v-for="issue in data.critical_issues"
            :key="issue.id"
          >
            <RouterLink
              :to="`/issues/${issue.id}`"
              class="flex flex-wrap items-center justify-between gap-2 rounded-md border border-banten-navy/10 px-3 py-3 text-sm hover:border-banten-gold/40"
            >
              <div>
                <span class="rounded bg-banten-red/10 px-2 py-0.5 text-xs font-semibold text-banten-red">
                  {{ issue.risk_level }}
                </span>
                <span class="ml-2 font-medium text-banten-navy">{{ issue.title }}</span>
              </div>
              <span class="text-xs text-banten-navy/50">{{ issue.status }}</span>
            </RouterLink>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
