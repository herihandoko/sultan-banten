<script setup>
import { onMounted, ref } from 'vue'
import api from '../services/api'
import PaginationBar from '../components/PaginationBar.vue'

const items = ref([])
const meta = ref(null)
const page = ref(1)
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)
const q = ref('')
const showInactive = ref(false)

const form = ref({ name: '', is_active: true })

function resetForm() {
  editingId.value = null
  form.value = { name: '', is_active: true }
  formError.value = ''
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/opds', {
      params: {
        active: showInactive.value ? '0' : '1',
        q: q.value || undefined,
        page: page.value,
        per_page: 15,
      },
    })
    items.value = data.data || []
    meta.value = data.meta || null
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat master OPD'
  } finally {
    loading.value = false
  }
}

function onPage(p) {
  page.value = p
  load()
}

function search() {
  page.value = 1
  load()
}

function editItem(item) {
  editingId.value = item.id
  form.value = { name: item.name, is_active: item.is_active }
  formError.value = ''
  showForm.value = true
}

async function save() {
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      await api.patch(`/opds/${editingId.value}`, form.value)
    } else {
      await api.post('/opds', form.value)
    }
    showForm.value = false
    resetForm()
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan OPD'
  } finally {
    saving.value = false
  }
}

async function deactivate(item) {
  if (!confirm(`Nonaktifkan "${item.name}"?`)) return
  await api.delete(`/opds/${item.id}`)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Master OPD</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          Referensi Organisasi Perangkat Daerah — dipakai saat buat user & validasi
        </p>
      </div>
      <button
        type="button"
        class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
        @click="showForm = !showForm; if (showForm) resetForm()"
      >
        {{ showForm ? 'Tutup' : '+ OPD' }}
      </button>
    </div>

    <div class="mb-4 flex flex-wrap items-center gap-3">
      <input
        v-model="q"
        type="search"
        placeholder="Cari nama OPD..."
        class="w-full max-w-sm rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
        @keyup.enter="search"
      />
      <button
        type="button"
        class="rounded-md border border-banten-navy/20 px-3 py-2 text-xs text-banten-navy hover:bg-white"
        @click="search"
      >
        Cari
      </button>
      <label class="flex items-center gap-2 text-xs text-banten-navy/70">
        <input v-model="showInactive" type="checkbox" class="rounded" @change="search" />
        Tampilkan nonaktif
      </label>
    </div>

    <form
      v-if="showForm"
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
      @submit.prevent="save"
    >
      <h2 class="font-display text-lg text-banten-navy">
        {{ editingId ? 'Edit OPD' : 'OPD Baru' }}
      </h2>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="md:col-span-2">
          <label class="text-sm font-medium text-banten-navy">Nama OPD</label>
          <input
            v-model="form.name"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div v-if="editingId" class="flex items-center gap-2 pt-2">
          <input id="opd_active" v-model="form.is_active" type="checkbox" class="rounded" />
          <label for="opd_active" class="text-sm text-banten-navy">Aktif</label>
        </div>
      </div>
      <p v-if="formError" class="mt-3 text-sm text-banten-red">{{ formError }}</p>
      <button
        type="submit"
        class="mt-4 rounded-md bg-banten-navy px-4 py-2 text-sm text-white disabled:opacity-60"
        :disabled="saving"
      >
        {{ saving ? 'Menyimpan...' : 'Simpan' }}
      </button>
    </form>

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <div v-else class="overflow-x-auto rounded-xl border border-banten-navy/10 bg-white/90">
      <table class="min-w-full text-left text-sm">
        <thead class="border-b border-banten-navy/10 bg-banten-sand/40 text-xs uppercase tracking-wide text-banten-navy/60">
          <tr>
            <th class="px-4 py-3 font-medium">ID</th>
            <th class="px-4 py-3 font-medium">Nama OPD</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b border-banten-navy/5 last:border-0">
            <td class="px-4 py-3 text-banten-navy/50">{{ item.source_id || item.id }}</td>
            <td class="px-4 py-3 font-medium text-banten-navy">{{ item.name }}</td>
            <td class="px-4 py-3">
              <span
                class="rounded px-2 py-0.5 text-xs font-semibold"
                :class="item.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-600'"
              >
                {{ item.is_active ? 'Aktif' : 'Nonaktif' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <div class="flex justify-end gap-3 text-xs">
                <button type="button" class="text-banten-gold hover:underline" @click="editItem(item)">
                  Edit
                </button>
                <button
                  v-if="item.is_active"
                  type="button"
                  class="text-banten-red hover:underline"
                  @click="deactivate(item)"
                >
                  Nonaktifkan
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!items.length" class="px-4 py-8 text-center text-sm text-banten-navy/50">
        Belum ada data OPD.
      </p>
    </div>
    <PaginationBar v-if="!loading && !error" :meta="meta" @update:page="onPage" />
  </div>
</template>
