<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'

const auth = useAuthStore()
const tab = ref('board') // board | stats
const missions = ref([])
const meta = ref(null)
const page = ref(1)
const stats = ref([])
const grandTotal = ref(0)
const issues = ref([])
const loading = ref(true)
const error = ref('')
const showCreate = ref(false)
const saving = ref(false)
const formError = ref('')
const joinForm = ref({}) // missionId -> { proof_url, notes }
const joiningId = ref(null)
const filters = ref({
  q: '',
  status: 'all',
  action_type: '',
})

const form = ref({
  title: '',
  instruction: '',
  target_url: '',
  action_type: 'like_share_comment',
  target_count: 50,
  issue_id: '',
})

const role = computed(() => auth.user?.role?.code)
const canCreate = computed(() =>
  ['super_admin', 'editor', 'media_kol_admin'].includes(role.value),
)
const canJoin = computed(() => ['super_admin', 'asn'].includes(role.value))
const canViewStats = computed(() =>
  ['super_admin', 'editor', 'pimpinan', 'media_kol_admin'].includes(role.value),
)

const actionLabel = {
  like: 'Like',
  share: 'Share',
  comment: 'Comment',
  like_share_comment: 'Like · Share · Comment',
}

const statusColor = {
  active: 'bg-emerald-100 text-emerald-800',
  completed: 'bg-sky-100 text-sky-800',
  cancelled: 'bg-slate-200 text-slate-600',
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, per_page: 10, status: filters.value.status || 'all' }
    if (filters.value.q) params.q = filters.value.q
    if (filters.value.action_type) params.action_type = filters.value.action_type
    const reqs = [
      api.get('/missions', { params }),
    ]
    if (canCreate.value) reqs.push(api.get('/missions/issues-options'))
    if (canViewStats.value && tab.value === 'stats') reqs.push(api.get('/missions/stats'))
    const results = await Promise.all(reqs)
    missions.value = results[0].data.data || []
    meta.value = results[0].data.meta || null
    if (canCreate.value && results[1]) issues.value = results[1].data.data || []
    if (canViewStats.value && tab.value === 'stats') {
      const statsRes = results[canCreate.value ? 2 : 1]
      if (statsRes) {
        stats.value = statsRes.data.data || []
        grandTotal.value = statsRes.data.grand_total || 0
      }
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat Mission Board'
  } finally {
    loading.value = false
  }
}

function onPage(p) {
  page.value = p
  load()
}

function applyFilters() {
  page.value = 1
  load()
}

function resetFilters() {
  filters.value = { q: '', status: 'all', action_type: '' }
  page.value = 1
  load()
}

async function loadStats() {
  tab.value = 'stats'
  try {
    const { data } = await api.get('/missions/stats')
    stats.value = data.data || []
    grandTotal.value = data.grand_total || 0
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat statistik'
  }
}

async function createMission() {
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      ...form.value,
      issue_id: form.value.issue_id ? Number(form.value.issue_id) : null,
      target_count: Number(form.value.target_count) || 0,
    }
    await api.post('/missions', payload)
    showCreate.value = false
    form.value = {
      title: '',
      instruction: '',
      target_url: '',
      action_type: 'like_share_comment',
      target_count: 50,
      issue_id: '',
    }
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal membuat misi'
  } finally {
    saving.value = false
  }
}

async function joinMission(mission) {
  joiningId.value = mission.id
  formError.value = ''
  try {
    const payload = joinForm.value[mission.id] || {}
    await api.post(`/missions/${mission.id}/join`, payload)
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal mencatat partisipasi'
  } finally {
    joiningId.value = null
  }
}

async function setStatus(mission, status) {
  await api.patch(`/missions/${mission.id}/status`, { status })
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Mission Board ASN</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          F.10 Instruksi amplifikasi · F.11 Log partisipasi
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <div v-if="canViewStats" class="flex gap-1 rounded-md border border-banten-navy/15 bg-white/70 p-1 text-xs">
          <button
            type="button"
            class="rounded px-3 py-1.5"
            :class="tab === 'board' ? 'bg-banten-navy text-white' : 'text-banten-navy/70'"
            @click="tab = 'board'"
          >
            Board
          </button>
          <button
            type="button"
            class="rounded px-3 py-1.5"
            :class="tab === 'stats' ? 'bg-banten-navy text-white' : 'text-banten-navy/70'"
            @click="loadStats"
          >
            Rekap OPD
          </button>
        </div>
        <button
          v-if="canCreate && tab === 'board'"
          type="button"
          class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
          @click="showCreate = !showCreate"
        >
          {{ showCreate ? 'Tutup' : '+ Buat Misi' }}
        </button>
      </div>
    </div>

    <form
      v-if="tab === 'board'"
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-4"
      @submit.prevent="applyFilters"
    >
      <div class="grid gap-3 md:grid-cols-4">
        <div class="md:col-span-2">
          <label class="text-xs font-medium text-banten-navy/70">Kata kunci</label>
          <input
            v-model="filters.q"
            type="search"
            placeholder="Judul, instruksi, URL..."
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Status</label>
          <select v-model="filters.status" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="all">Semua</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Aksi</label>
          <select v-model="filters.action_type" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option v-for="(label, key) in actionLabel" :key="key" :value="key">{{ label }}</option>
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

    <div v-if="loading && tab === 'board'" class="text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>

    <template v-else-if="tab === 'stats'">
      <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
        <p class="text-sm text-banten-navy/65">Total partisipasi: <strong>{{ grandTotal }}</strong></p>
        <div v-if="!stats.length" class="mt-4 text-sm text-banten-navy/60">Belum ada data partisipasi.</div>
        <ul v-else class="mt-4 space-y-2">
          <li
            v-for="s in stats"
            :key="s.opd_name"
            class="flex items-center justify-between rounded-md border border-banten-navy/10 px-3 py-2 text-sm"
          >
            <span class="text-banten-navy">{{ s.opd_name }}</span>
            <span class="font-semibold text-banten-navy">{{ s.total }}</span>
          </li>
        </ul>
      </div>
    </template>

    <template v-else>
      <form
        v-if="showCreate && canCreate"
        class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
        @submit.prevent="createMission"
      >
        <h2 class="font-display text-lg text-banten-navy">Misi Amplifikasi Baru</h2>
        <div class="mt-4 grid gap-3 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="text-sm font-medium text-banten-navy">Judul misi</label>
            <input v-model="form.title" required class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-2">
            <label class="text-sm font-medium text-banten-navy">Instruksi</label>
            <textarea
              v-model="form.instruction"
              required
              rows="3"
              class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              placeholder="Like, share, dan komentar dengan narasi positif..."
            />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">URL target</label>
            <input v-model="form.target_url" type="url" placeholder="https://..." class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Aksi</label>
            <select v-model="form.action_type" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="like_share_comment">Like · Share · Comment</option>
              <option value="like">Like</option>
              <option value="share">Share</option>
              <option value="comment">Comment</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Target partisipan</label>
            <input v-model="form.target_count" type="number" min="0" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-banten-navy">Isu terkait (opsional)</label>
            <select v-model="form.issue_id" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
              <option value="">— tidak terkait —</option>
              <option v-for="i in issues" :key="i.id" :value="i.id">{{ i.risk_level }} · {{ i.title }}</option>
            </select>
          </div>
        </div>
        <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
        <button type="submit" class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60" :disabled="saving">
          {{ saving ? 'Menyimpan...' : 'Publikasikan Misi' }}
        </button>
      </form>

      <div
        v-if="!missions.length"
        class="rounded-xl border border-dashed border-banten-navy/20 bg-white/60 px-6 py-16 text-center"
      >
        <p class="font-display text-xl text-banten-navy">Belum ada misi</p>
        <p class="mt-2 text-sm text-banten-navy/60">Admin/editor dapat membuat misi amplifikasi harian.</p>
      </div>

      <div v-else class="space-y-4">
        <article
          v-for="m in missions"
          :key="m.id"
          class="rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="statusColor[m.status]">
                  {{ m.status }}
                </span>
                <span class="text-xs text-banten-navy/50">{{ actionLabel[m.action_type] || m.action_type }}</span>
              </div>
              <h2 class="mt-2 font-display text-xl text-banten-navy">{{ m.title }}</h2>
              <p class="mt-2 whitespace-pre-wrap text-sm text-banten-navy/75">{{ m.instruction }}</p>
              <a
                v-if="m.target_url"
                :href="m.target_url"
                target="_blank"
                rel="noopener"
                class="mt-2 inline-block text-sm text-banten-gold hover:underline"
              >
                Buka tautan target →
              </a>
              <p class="mt-2 text-xs text-banten-navy/55">
                Partisipasi: {{ m.participation_count || 0 }}
                <span v-if="m.target_count"> / {{ m.target_count }}</span>
              </p>
            </div>
            <div v-if="canCreate && m.status === 'active'" class="flex gap-2 text-xs">
              <button type="button" class="rounded border border-banten-navy/20 px-2 py-1 text-banten-navy" @click="setStatus(m, 'completed')">
                Selesai
              </button>
              <button type="button" class="rounded border border-banten-red/30 px-2 py-1 text-banten-red" @click="setStatus(m, 'cancelled')">
                Batalkan
              </button>
            </div>
          </div>

          <div
            v-if="canJoin && m.status === 'active' && !m.joined"
            class="mt-4 rounded-lg border border-banten-navy/10 bg-banten-sand/40 p-4"
          >
            <p class="text-sm font-medium text-banten-navy">Catat partisipasi Anda</p>
            <div class="mt-2 grid gap-2 md:grid-cols-2">
              <input
                :value="joinForm[m.id]?.proof_url || ''"
                type="url"
                placeholder="URL bukti (opsional)"
                class="rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
                @input="joinForm[m.id] = { ...(joinForm[m.id] || {}), proof_url: $event.target.value }"
              />
              <input
                :value="joinForm[m.id]?.notes || ''"
                placeholder="Catatan (opsional)"
                class="rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
                @input="joinForm[m.id] = { ...(joinForm[m.id] || {}), notes: $event.target.value }"
              />
            </div>
            <button
              type="button"
              class="mt-3 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60"
              :disabled="joiningId === m.id"
              @click="joinMission(m)"
            >
              {{ joiningId === m.id ? 'Menyimpan...' : 'Saya Sudah Amplifikasi' }}
            </button>
          </div>
          <p v-else-if="m.joined" class="mt-3 text-sm text-emerald-700">✓ Anda sudah berpartisipasi</p>

          <details v-if="m.participations?.length" class="mt-3">
            <summary class="cursor-pointer text-xs text-banten-gold">
              Lihat log partisipasi ({{ m.participations.length }})
            </summary>
            <ul class="mt-2 max-h-40 space-y-1 overflow-y-auto text-xs text-banten-navy/70">
              <li v-for="p in m.participations" :key="p.id">
                {{ p.user_name || `User #${p.user_id}` }}
                <span v-if="p.opd_name"> · {{ p.opd_name }}</span>
                · {{ p.completed_at }}
              </li>
            </ul>
          </details>
        </article>
      </div>
      <PaginationBar :meta="meta" @update:page="onPage" />
    </template>
  </div>
</template>
