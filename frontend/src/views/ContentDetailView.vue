<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()

const item = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const formError = ref('')
const editForm = ref({ title: '', body: '', media_url: '', content_type: 'text_release' })
const reviewNotes = ref('')

const statusColor = {
  draft: 'bg-slate-200 text-slate-700',
  in_review: 'bg-amber-100 text-amber-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
  published: 'bg-sky-100 text-sky-800',
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
  formError.value = ''
  try {
    const { data } = await api.patch(`/content/${route.params.id}`, editForm.value)
    item.value = data.data
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan'
  } finally {
    saving.value = false
  }
}

async function submitReview() {
  saving.value = true
  formError.value = ''
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
            <span class="rounded px-2 py-0.5 text-xs font-semibold" :class="statusColor[item.status]">
              {{ item.status }}
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
            class="rounded-xl border border-banten-gold/30 bg-amber-50/50 p-5"
          >
            <h2 class="font-display text-lg text-banten-navy">Acuan Mata Bathin</h2>
            <p class="mt-2 text-sm text-banten-navy/80 whitespace-pre-wrap">
              {{ item.issue.narrative_card?.statement || item.issue.summary }}
            </p>
          </div>

          <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
            <h2 class="font-display text-lg text-banten-navy">
              {{ isEditable && canEdit ? 'Edit Draft' : 'Naskah Konten' }}
            </h2>

            <template v-if="isEditable && canEdit">
              <label class="mt-4 block text-sm font-medium text-banten-navy">Judul</label>
              <input
                v-model="editForm.title"
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              />
              <label class="mt-3 block text-sm font-medium text-banten-navy">Tipe</label>
              <select
                v-model="editForm.content_type"
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              >
                <option value="text_release">Rilis Teks</option>
                <option value="infographic">Infografis</option>
                <option value="video">Video</option>
              </select>
              <label class="mt-3 block text-sm font-medium text-banten-navy">Isi</label>
              <textarea
                v-model="editForm.body"
                rows="10"
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              />
              <label class="mt-3 block text-sm font-medium text-banten-navy">URL media</label>
              <input
                v-model="editForm.media_url"
                class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              />
              <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
              <div class="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  class="rounded-md border border-banten-navy/20 px-4 py-2 text-sm text-banten-navy disabled:opacity-60"
                  :disabled="saving"
                  @click="save"
                >
                  Simpan
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
              <p class="mt-3 whitespace-pre-wrap text-sm text-banten-navy/85">
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

          <div class="rounded-xl border border-banten-navy/10 bg-white/80 p-5">
            <h2 class="font-display text-lg text-banten-navy">Riwayat Approval</h2>
            <div v-if="!item.approvals?.length" class="mt-2 text-sm text-banten-navy/60">
              Belum ada keputusan.
            </div>
            <ul v-else class="mt-3 space-y-2">
              <li
                v-for="a in item.approvals"
                :key="a.id"
                class="rounded-md border border-banten-navy/10 px-3 py-2 text-sm"
              >
                <span
                  class="rounded px-2 py-0.5 text-xs font-semibold"
                  :class="a.decision === 'approved' ? statusColor.approved : statusColor.rejected"
                >
                  {{ a.decision }}
                </span>
                <p v-if="a.notes" class="mt-1 text-banten-navy/75">{{ a.notes }}</p>
                <p class="mt-1 text-xs text-banten-navy/45">{{ a.decided_at }}</p>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
