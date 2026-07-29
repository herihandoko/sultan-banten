<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'

const auth = useAuthStore()
const items = ref([])
const meta = ref(null)
const page = ref(1)
const loading = ref(true)
const error = ref('')
const filter = ref('waiting')
const activeId = ref(null)
const responding = ref(false)
const responseForm = ref({
  status: 'validated',
  response_notes: '',
})
const formError = ref('')

const statusColor = {
  waiting: 'bg-amber-100 text-amber-800',
  validated: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
}

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
    if (filter.value !== 'all') params.status = filter.value
    const { data } = await api.get('/validations', { params })
    items.value = data.data || []
    meta.value = data.meta || null
    if (activeId.value && !items.value.find((i) => i.id === activeId.value)) {
      activeId.value = null
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat validasi OPD'
  } finally {
    loading.value = false
  }
}

function setFilter(f) {
  filter.value = f
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

function openRespond(item) {
  activeId.value = item.id
  responseForm.value = { status: 'validated', response_notes: '' }
  formError.value = ''
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Validasi OPD</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          F.03 — Verifikasi data isu ke OPD teknis terkait
        </p>
      </div>
      <div class="flex gap-1 rounded-md border border-banten-navy/15 bg-white/70 p-1 text-xs">
        <button
          v-for="f in [
            { key: 'waiting', label: 'Waiting' },
            { key: 'validated', label: 'Validated' },
            { key: 'rejected', label: 'Rejected' },
            { key: 'all', label: 'Semua' },
          ]"
          :key="f.key"
          type="button"
          class="rounded px-3 py-1.5 transition"
          :class="filter === f.key ? 'bg-banten-navy text-white' : 'text-banten-navy/70 hover:bg-banten-sand'"
          @click="setFilter(f.key)"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <div
      v-else-if="!items.length"
      class="rounded-xl border border-dashed border-banten-navy/20 bg-white/60 px-6 py-16 text-center"
    >
      <p class="font-display text-xl text-banten-navy">Tidak ada permintaan validasi</p>
      <p class="mt-2 text-sm text-banten-navy/60">
        Permintaan dari Crisis Room akan muncul di sini.
      </p>
    </div>
    <div v-else class="space-y-3">
      <article
        v-for="item in items"
        :key="item.id"
        class="rounded-xl border border-banten-navy/10 bg-white/80 px-5 py-4"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="statusColor[item.status]">
                {{ item.status }}
              </span>
              <span class="text-xs text-banten-navy/50">{{ item.opd_name }}</span>
            </div>
            <h2 class="mt-2 font-display text-xl text-banten-navy">
              {{ item.issue?.title || `Isu #${item.issue_id}` }}
            </h2>
            <p class="mt-1 line-clamp-2 text-sm text-banten-navy/70">
              {{ item.request_notes || item.issue?.summary || 'Tanpa catatan permintaan' }}
            </p>
            <div v-if="item.issue?.evidence?.length" class="mt-2 text-xs text-banten-navy/55">
              Evidence dilampirkan: {{ item.issue.evidence.length }} berkas
            </div>
          </div>
          <div class="flex flex-col items-end gap-2">
            <RouterLink
              :to="`/issues/${item.issue_id}`"
              class="text-xs text-banten-gold hover:underline"
            >
              Lihat isu
            </RouterLink>
            <button
              v-if="canRespond && item.status === 'waiting'"
              type="button"
              class="rounded-md bg-banten-navy px-3 py-1.5 text-xs text-white hover:bg-banten-navy-dark"
              @click="openRespond(item)"
            >
              Respon
            </button>
          </div>
        </div>

        <div
          v-if="activeId === item.id"
          class="mt-4 rounded-lg border border-banten-navy/10 bg-banten-sand/40 p-4"
        >
          <p class="text-sm font-medium text-banten-navy">Respon Validasi</p>
          <div class="mt-3 flex gap-3 text-sm">
            <label class="flex items-center gap-2">
              <input v-model="responseForm.status" type="radio" value="validated" />
              Validated
            </label>
            <label class="flex items-center gap-2">
              <input v-model="responseForm.status" type="radio" value="rejected" />
              Rejected
            </label>
          </div>
          <textarea
            v-model="responseForm.response_notes"
            rows="3"
            class="mt-3 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
            placeholder="Catatan hasil verifikasi..."
          />
          <p v-if="formError" class="mt-2 text-sm text-banten-red">{{ formError }}</p>
          <div class="mt-3 flex gap-2">
            <button
              type="button"
              class="rounded-md bg-banten-navy px-3 py-1.5 text-sm text-white disabled:opacity-60"
              :disabled="responding"
              @click="respond"
            >
              {{ responding ? 'Mengirim...' : 'Kirim Respon' }}
            </button>
            <button
              type="button"
              class="rounded-md border border-banten-navy/20 px-3 py-1.5 text-sm text-banten-navy"
              @click="activeId = null"
            >
              Batal
            </button>
          </div>
        </div>

        <p v-if="item.response_notes && item.status !== 'waiting'" class="mt-3 text-sm text-banten-navy/75">
          <span class="font-medium">Respon:</span> {{ item.response_notes }}
        </p>
      </article>
    </div>
    <PaginationBar :meta="meta" @update:page="onPage" />
  </div>
</template>
