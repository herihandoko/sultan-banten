<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import ContentDraftFields from '../components/ContentDraftFields.vue'

const route = useRoute()
const auth = useAuthStore()

const item = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const formError = ref('')
const formNotice = ref('')
const savePending = ref(false)
const editForm = ref({ title: '', body: '', media_url: '', content_type: 'text_release' })
const reviewNotes = ref('')

const statusMeta = {
  draft: { label: 'Draft', chip: 'border border-slate-500/40 bg-slate-500/10 text-slate-300' },
  in_review: { label: 'Review', chip: 'border border-amber-500/40 bg-amber-500/10 text-amber-300' },
  approved: { label: 'Disetujui', chip: 'border border-emerald-500/40 bg-emerald-500/10 text-emerald-300' },
  rejected: { label: 'Ditolak', chip: 'border border-rose-500/40 bg-rose-500/10 text-rose-300' },
  published: { label: 'Terbit', chip: 'border border-sky-500/40 bg-sky-500/10 text-sky-300' },
}

function statusOf(status) {
  return statusMeta[status] || {
    label: status || '—',
    chip: 'border border-[#30363d] text-[#c9d1d9]',
  }
}

const typeLabel = {
  text_release: 'Rilis Teks',
  infographic: 'Infografis',
  video: 'Video',
}

const role = computed(() => auth.user?.role?.code)
const canEdit = computed(() => ['super_admin', 'editor'].includes(role.value))
const canApprove = computed(() => ['super_admin', 'pimpinan'].includes(role.value))
const isEditable = computed(() => item.value && ['draft', 'rejected'].includes(item.value.status))

const approvals = computed(() => {
  const list = item.value?.approvals || []
  return [...list].sort((a, b) => String(b.decided_at || '').localeCompare(String(a.decided_at || '')))
})

function decisionMeta(decision) {
  if (decision === 'approved') {
    return {
      label: 'Disetujui',
      chip: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
      dot: 'bg-emerald-400',
    }
  }
  return {
    label: 'Ditolak',
    chip: 'border-rose-500/40 bg-rose-500/10 text-rose-300',
    dot: 'bg-rose-400',
  }
}

function formatDateTime(iso) {
  if (!iso) return ''
  const normalized = /[zZ]|[+-]\d{2}:\d{2}$/.test(iso) ? iso : `${iso}Z`
  const d = new Date(normalized)
  if (Number.isNaN(d.getTime())) return iso
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

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/content/${route.params.id}`)
    item.value = data.data
    editForm.value = {
      title: item.value.title,
      body: item.value.body || '',
      media_url: item.value.media_url || '',
      content_type: item.value.content_type,
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat konten'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  savePending.value = true
  formError.value = ''
  formNotice.value = ''
  try {
    const { data } = await api.patch(`/content/${route.params.id}`, editForm.value)
    item.value = data.data
    formNotice.value = 'Draft tersimpan.'
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan'
  } finally {
    saving.value = false
    savePending.value = false
  }
}

async function submitReview() {
  saving.value = true
  formError.value = ''
  formNotice.value = ''
  try {
    if (isEditable.value) {
      await api.patch(`/content/${route.params.id}`, editForm.value)
    }
    const { data } = await api.post(`/content/${route.params.id}/submit`)
    item.value = data.data
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal mengajukan review'
  } finally {
    saving.value = false
  }
}

async function decide(decision) {
  saving.value = true
  formError.value = ''
  try {
    const { data } = await api.post(`/content/${route.params.id}/approve`, {
      decision,
      notes: reviewNotes.value,
    })
    item.value = data.data
    reviewNotes.value = ''
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal memproses approval'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <RouterLink to="/konten" class="text-sm text-banten-navy/60 hover:text-banten-navy">
      ← Kembali ke Hub Konten
    </RouterLink>

    <div v-if="loading" class="mt-6 text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="mt-6 rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <template v-else-if="item">
      <div class="mt-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="rounded-md px-2 py-0.5 text-xs font-semibold" :class="statusOf(item.status).chip">
              {{ statusOf(item.status).label }}
            </span>
            <span class="text-xs text-banten-navy/50">{{ typeLabel[item.content_type] }}</span>
          </div>
          <h1 class="mt-2 font-display text-3xl text-banten-navy">{{ item.title }}</h1>
          <p class="mt-1 text-sm text-banten-navy/65">
            Isu:
            <RouterLink :to="`/issues/${item.issue_id}`" class="text-banten-gold hover:underline">
              {{ item.issue?.title || `#${item.issue_id}` }}
            </RouterLink>
          </p>
        </div>
      </div>

      <div class="mt-6 grid gap-4 lg:grid-cols-3">
        <section class="space-y-4 lg:col-span-2">
          <div
            v-if="item.issue?.narrative_card || item.issue?.summary"
            class="issue-brief rounded-xl border border-banten-gold/30 bg-amber-50/60 p-5"
          >
            <h2 class="issue-brief-title font-display text-lg">Acuan narasi</h2>
            <p class="mt-2 whitespace-pre-wrap text-sm">
              {{ item.issue.narrative_card?.statement || item.issue.summary }}
            </p>
          </div>

          <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
            <h2 class="font-display text-lg text-banten-navy">
              {{ isEditable && canEdit ? 'Edit Draft' : 'Naskah Konten' }}
            </h2>

            <template v-if="isEditable && canEdit">
              <div class="mt-4 grid gap-3 md:grid-cols-2">
                <ContentDraftFields
                  v-model:content-type="editForm.content_type"
                  v-model:title="editForm.title"
                  v-model:body="editForm.body"
                  v-model:media-url="editForm.media_url"
                />
              </div>
              <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
              <p
                v-if="formNotice"
                class="mt-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800"
              >
                {{ formNotice }}
              </p>
              <div class="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  class="rounded-md border border-banten-navy/20 px-4 py-2 text-sm text-banten-navy disabled:opacity-60"
                  :disabled="saving"
                  @click="save"
                >
                  {{ savePending ? 'Menyimpan...' : 'Simpan' }}
                </button>
                <button
                  type="button"
                  class="rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60"
                  :disabled="saving"
                  @click="submitReview"
                >
                  Ajukan Review
                </button>
              </div>
            </template>

            <template v-else>
              <p class="mt-3 whitespace-pre-wrap text-sm text-banten-navy">
                {{ item.body || '—' }}
              </p>
              <a
                v-if="item.media_url"
                :href="item.media_url"
                target="_blank"
                rel="noopener"
                class="mt-3 inline-block text-sm text-banten-gold hover:underline"
              >
                {{ item.media_url }}
              </a>
              <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
            </template>
          </div>
        </section>

        <section class="space-y-4">
          <div
            v-if="canApprove && item.status === 'in_review'"
            class="rounded-xl border border-banten-navy/10 bg-white/80 p-5"
          >
            <h2 class="font-display text-lg text-banten-navy">Approval Pimpinan</h2>
            <textarea
              v-model="reviewNotes"
              rows="3"
              class="mt-3 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              placeholder="Catatan review..."
            />
            <div class="mt-3 flex gap-2">
              <button
                type="button"
                class="flex-1 rounded-md bg-emerald-700 px-3 py-2 text-sm text-white disabled:opacity-60"
                :disabled="saving"
                @click="decide('approved')"
              >
                Approve
              </button>
              <button
                type="button"
                class="flex-1 rounded-md bg-banten-red px-3 py-2 text-sm text-white disabled:opacity-60"
                :disabled="saving"
                @click="decide('rejected')"
              >
                Reject
              </button>
            </div>
          </div>

          <div
            v-if="['approved', 'published'].includes(item.status) && canEdit"
            class="rounded-xl border border-banten-navy/10 bg-white/80 p-5"
          >
            <h2 class="font-display text-lg text-banten-navy">Diseminasi</h2>
            <p class="mt-1 text-xs text-banten-navy/60">F.08 — Kirim ke media mitra</p>
            <RouterLink
              to="/media-hub"
              class="mt-3 inline-block rounded-md bg-banten-red px-3 py-2 text-sm text-white hover:opacity-90"
            >
              Buka Media Blast
            </RouterLink>
          </div>

          <div class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
            <h2 class="text-base font-semibold text-white">Riwayat Approval</h2>
            <p class="mt-1 text-[11px] text-[#6e7681]">Keputusan pimpinan atas naskah ini</p>
            <p v-if="!approvals.length" class="mt-4 text-sm text-[#8b949e]">Belum ada keputusan.</p>
            <ol v-else class="mt-4 space-y-3">
              <li v-for="a in approvals" :key="a.id" class="relative pl-4">
                <span
                  class="absolute left-0 top-3 h-2 w-2 rounded-full"
                  :class="decisionMeta(a.decision).dot"
                  aria-hidden="true"
                />
                <div class="rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2.5">
                  <span
                    class="inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold"
                    :class="decisionMeta(a.decision).chip"
                  >
                    {{ decisionMeta(a.decision).label }}
                  </span>
                  <p class="mt-2 text-sm leading-relaxed text-[#e6edf3]">
                    {{ a.notes || 'Tanpa catatan.' }}
                  </p>
                  <p class="mt-2 text-[11px] text-[#6e7681]">
                    {{ a.reviewer_name || 'Pimpinan' }}
                    <span v-if="a.decided_at"> · {{ formatDateTime(a.decided_at) }}</span>
                  </p>
                </div>
              </li>
            </ol>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
