<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()

const issue = ref(null)
const loading = ref(true)
const error = ref('')
const masterOpds = ref([])
const opdAdmins = ref([])
const submitting = ref(false)
const formError = ref('')
const form = ref({
  opd_id: '',
  assigned_to: '',
  request_notes: '',
})

const riskColor = {
  R0: 'bg-slate-200 text-slate-700',
  R1: 'bg-sky-100 text-sky-800',
  R2: 'bg-amber-100 text-amber-800',
  R3: 'bg-orange-100 text-orange-800',
  R4: 'bg-red-100 text-red-800',
  R5: 'bg-banten-red text-white',
}

const statusColor = {
  waiting: 'bg-amber-100 text-amber-800',
  validated: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
}

const canRequest = computed(() => {
  const code = auth.user?.role?.code
  return code === 'super_admin' || code === 'editor'
})

const filteredAdmins = computed(() => {
  const opd = masterOpds.value.find((o) => String(o.id) === String(form.value.opd_id))
  if (!opd) return opdAdmins.value
  return opdAdmins.value.filter((a) => a.opd_name === opd.name)
})

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

async function requestValidation() {
  submitting.value = true
  formError.value = ''
  try {
    const payload = {
      opd_id: Number(form.value.opd_id),
      request_notes: form.value.request_notes,
    }
    if (form.value.assigned_to) payload.assigned_to = Number(form.value.assigned_to)
    await api.post(`/validations/issues/${route.params.id}`, payload)
    form.value.request_notes = ''
    form.value.assigned_to = ''
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal mengirim validasi'
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <RouterLink to="/crisis-room" class="text-sm text-banten-navy/60 hover:text-banten-navy">
      ← Kembali ke Crisis Room
    </RouterLink>

    <div v-if="loading" class="mt-6 text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="mt-6 rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <template v-else-if="issue">
      <div class="mt-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="riskColor[issue.risk_level]">
              {{ issue.risk_level }}
            </span>
            <span class="rounded-md bg-banten-sand px-2.5 py-1 text-xs font-medium text-banten-navy">
              {{ issue.status }}
            </span>
            <span class="text-xs uppercase text-banten-navy/45">{{ issue.source }}</span>
          </div>
          <h1 class="mt-2 font-display text-3xl text-banten-navy">{{ issue.title }}</h1>
        </div>
      </div>

      <div class="mt-6 grid gap-4 lg:grid-cols-3">
        <section class="space-y-4 lg:col-span-2">
          <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
            <h2 class="font-display text-lg text-banten-navy">Issue Brief</h2>
            <p class="mt-2 text-sm text-banten-navy/80 whitespace-pre-wrap">
              {{ issue.summary || 'Belum ada ringkasan.' }}
            </p>
            <p v-if="issue.why_now" class="mt-3 text-sm">
              <span class="font-medium text-banten-navy">Why now:</span>
              <span class="text-banten-navy/75"> {{ issue.why_now }}</span>
            </p>
            <div v-if="issue.recommended_actions?.length" class="mt-3">
              <p class="text-sm font-medium text-banten-navy">Rekomendasi Mata Bathin</p>
              <ul class="mt-1 list-disc pl-5 text-sm text-banten-navy/75">
                <li v-for="(a, i) in issue.recommended_actions" :key="i">{{ a }}</li>
              </ul>
            </div>
          </div>

          <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
            <h2 class="font-display text-lg text-banten-navy">Evidence Pack</h2>
            <div v-if="!issue.evidence?.length" class="mt-2 text-sm text-banten-navy/60">
              Belum ada evidence.
            </div>
            <ul v-else class="mt-3 space-y-2">
              <li
                v-for="e in issue.evidence"
                :key="e.id"
                class="rounded-md border border-banten-navy/10 px-3 py-2 text-sm"
              >
                <p class="font-medium text-banten-navy">{{ e.title || e.source_name || 'Evidence' }}</p>
                <a
                  v-if="e.url"
                  :href="e.url"
                  target="_blank"
                  rel="noopener"
                  class="text-xs text-banten-gold hover:underline"
                >
                  {{ e.url }}
                </a>
                <p v-if="e.snippet" class="mt-1 text-banten-navy/65">{{ e.snippet }}</p>
              </li>
            </ul>
          </div>
        </section>

        <section class="space-y-4">
          <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
            <h2 class="font-display text-lg text-banten-navy">Validasi OPD</h2>
            <p class="mt-1 text-xs text-banten-navy/60">F.03 — Waiting → Validated → Rejected</p>

            <div v-if="issue.validations?.length" class="mt-4 space-y-3">
              <div
                v-for="v in issue.validations"
                :key="v.id"
                class="rounded-md border border-banten-navy/10 px-3 py-3"
              >
                <div class="flex items-center justify-between gap-2">
                  <p class="text-sm font-medium text-banten-navy">{{ v.opd_name }}</p>
                  <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="statusColor[v.status]">
                    {{ v.status }}
                  </span>
                </div>
                <p v-if="v.request_notes" class="mt-1 text-xs text-banten-navy/65">{{ v.request_notes }}</p>
                <p v-if="v.response_notes" class="mt-2 text-xs text-banten-navy/80">
                  <span class="font-medium">Respon:</span> {{ v.response_notes }}
                </p>
              </div>
            </div>
            <p v-else class="mt-3 text-sm text-banten-navy/60">Belum ada permintaan validasi.</p>

            <form v-if="canRequest" class="mt-5 border-t border-banten-navy/10 pt-4" @submit.prevent="requestValidation">
              <p class="text-sm font-medium text-banten-navy">Kirim ke OPD</p>
              <label class="mt-3 block text-xs text-banten-navy/70">OPD (master)</label>
              <select
                v-model="form.opd_id"
                required
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
                @change="form.assigned_to = ''"
              >
                <option value="">— pilih OPD —</option>
                <option v-for="o in masterOpds" :key="o.id" :value="o.id">{{ o.name }}</option>
              </select>
              <label class="mt-3 block text-xs text-banten-navy/70">OPD Admin (opsional)</label>
              <select
                v-model="form.assigned_to"
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              >
                <option value="">— auto-assign bila ada —</option>
                <option v-for="o in filteredAdmins" :key="o.id" :value="o.id">
                  {{ o.full_name }}
                </option>
              </select>
              <label class="mt-3 block text-xs text-banten-navy/70">Catatan permintaan</label>
              <textarea
                v-model="form.request_notes"
                rows="3"
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
                placeholder="Mohon verifikasi data terkait isu ini..."
              />
              <p v-if="formError" class="mt-2 text-sm text-banten-red">{{ formError }}</p>
              <button
                type="submit"
                class="mt-3 w-full rounded-md bg-banten-navy px-3 py-2 text-sm text-white disabled:opacity-60"
                :disabled="submitting"
              >
                {{ submitting ? 'Mengirim...' : 'Kirim Permintaan Validasi' }}
              </button>
            </form>
          </div>
          <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
            <div class="flex items-center justify-between gap-2">
              <div>
                <h2 class="font-display text-lg text-banten-navy">Konten Klarifikasi</h2>
                <p class="mt-1 text-xs text-banten-navy/60">F.04 — Draft → Review → Approve</p>
              </div>
              <RouterLink
                v-if="canRequest"
                :to="`/konten?issue_id=${issue.id}`"
                class="rounded-md bg-banten-navy px-3 py-1.5 text-xs text-white hover:bg-banten-navy-dark"
              >
                + Buat
              </RouterLink>
            </div>
            <div v-if="issue.content_items?.length" class="mt-4 space-y-2">
              <RouterLink
                v-for="c in issue.content_items"
                :key="c.id"
                :to="`/konten/${c.id}`"
                class="block rounded-md border border-banten-navy/10 px-3 py-2 text-sm hover:border-banten-gold/40"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="font-medium text-banten-navy">{{ c.title }}</span>
                  <span class="text-xs text-banten-navy/55">{{ c.status }}</span>
                </div>
              </RouterLink>
            </div>
            <p v-else class="mt-3 text-sm text-banten-navy/60">Belum ada konten untuk isu ini.</p>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
