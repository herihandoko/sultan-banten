<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import PaginationBar from '../components/PaginationBar.vue'
import SearchableSelect from '../components/SearchableSelect.vue'

const auth = useAuthStore()
const users = ref([])
const meta = ref(null)
const page = ref(1)
const roles = ref([])
const opds = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)
const showPassword = ref(false)
const filters = ref({
  q: '',
  role_code: '',
  active: '',
  opd_id: '',
  sort_by: 'created_at',
  sort_dir: 'desc',
})

const opdOptions = computed(() =>
  opds.value.map((o) => ({ value: o.id, label: o.name })),
)

const filterOpdOptions = computed(() => [
  { value: '', label: 'Semua OPD' },
  ...opdOptions.value,
])

const sortOptions = [
  { value: 'created_at', label: 'Terbaru dibuat' },
  { value: 'full_name', label: 'Nama' },
  { value: 'username', label: 'Username' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'No. HP' },
  { value: 'role', label: 'Role' },
  { value: 'opd_name', label: 'OPD' },
  { value: 'is_active', label: 'Status' },
]

const form = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  phone: '',
  role_code: 'editor',
  opd_id: '',
  is_active: true,
})

const isAdmin = computed(() => auth.user?.role?.code === 'super_admin')
const needsOpd = computed(() => ['opd_admin', 'asn'].includes(form.value.role_code))

function resetForm() {
  editingId.value = null
  showPassword.value = false
  form.value = {
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone: '',
    role_code: 'editor',
    opd_id: '',
    is_active: true,
  }
  formError.value = ''
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, per_page: 10 }
    for (const [k, v] of Object.entries(filters.value)) {
      if (v) params[k] = v
    }
    const [usersRes, rolesRes, opdsRes] = await Promise.all([
      api.get('/users', { params }),
      api.get('/users/roles'),
      api.get('/opds', { params: { active: '1', per_page: 200 } }),
    ])
    users.value = usersRes.data.data || []
    meta.value = usersRes.data.meta || null
    roles.value = rolesRes.data.data || []
    opds.value = opdsRes.data.data || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal memuat pengguna'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  load()
}

function resetFilters() {
  filters.value = {
    q: '',
    role_code: '',
    active: '',
    opd_id: '',
    sort_by: 'created_at',
    sort_dir: 'desc',
  }
  page.value = 1
  load()
}

function onSortChange() {
  page.value = 1
  load()
}

function toggleSortDir() {
  filters.value.sort_dir = filters.value.sort_dir === 'asc' ? 'desc' : 'asc'
  page.value = 1
  load()
}

function onPage(p) {
  page.value = p
  load()
}

function editUser(user) {
  editingId.value = user.id
  form.value = {
    username: user.username,
    email: user.email,
    password: '',
    full_name: user.full_name,
    phone: user.phone || '',
    role_code: user.role?.code || 'editor',
    opd_id: user.opd_id || '',
    is_active: user.is_active,
  }
  formError.value = ''
  showForm.value = true
}

async function save() {
  saving.value = true
  formError.value = ''
  try {
    const opdPayload = needsOpd.value
      ? { opd_id: form.value.opd_id ? Number(form.value.opd_id) : null }
      : { opd_id: form.value.opd_id ? Number(form.value.opd_id) : null, opd_name: form.value.opd_id ? undefined : '' }

    if (editingId.value) {
      const payload = {
        full_name: form.value.full_name,
        phone: form.value.phone,
        email: form.value.email,
        role_code: form.value.role_code,
        is_active: form.value.is_active,
        ...opdPayload,
      }
      if (!form.value.opd_id) {
        payload.opd_id = null
        payload.opd_name = ''
      }
      if (form.value.password) payload.password = form.value.password
      await api.patch(`/users/${editingId.value}`, payload)
    } else {
      await api.post('/users', {
        username: form.value.username,
        email: form.value.email,
        password: form.value.password,
        full_name: form.value.full_name,
        phone: form.value.phone || null,
        role_code: form.value.role_code,
        opd_id: form.value.opd_id ? Number(form.value.opd_id) : null,
      })
    }
    showForm.value = false
    resetForm()
    await load()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Gagal menyimpan pengguna'
  } finally {
    saving.value = false
  }
}

async function toggleActive(user) {
  if (user.id === auth.user?.id) {
    alert('Tidak bisa menonaktifkan akun sendiri')
    return
  }
  await api.patch(`/users/${user.id}`, { is_active: !user.is_active })
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl text-banten-navy">Manajemen User</h1>
        <p class="mt-1 text-sm text-banten-navy/65">
          Tambah pengguna dan atur role RBAC (super admin)
        </p>
      </div>
      <button
        v-if="isAdmin"
        type="button"
        class="rounded-md bg-banten-navy px-3 py-2 text-xs text-white"
        @click="showForm = !showForm; if (showForm) resetForm()"
      >
        {{ showForm ? 'Tutup' : '+ User' }}
      </button>
    </div>

    <form
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-4"
      @submit.prevent="applyFilters"
    >
      <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        <div class="md:col-span-2 lg:col-span-3">
          <label class="text-xs font-medium text-banten-navy/70">Kata kunci</label>
          <input
            v-model="filters.q"
            type="search"
            placeholder="Nama, username, email, no HP, OPD..."
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Role</label>
          <select v-model="filters.role_code" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option v-for="r in roles" :key="r.id" :value="r.code">{{ r.name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Status</label>
          <select v-model="filters.active" class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm">
            <option value="">Semua</option>
            <option value="1">Aktif</option>
            <option value="0">Nonaktif</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">OPD</label>
          <SearchableSelect
            v-model="filters.opd_id"
            tone="dark"
            :options="filterOpdOptions"
            placeholder="Semua OPD"
            search-placeholder="Cari OPD..."
          />
        </div>
        <div>
          <label class="text-xs font-medium text-banten-navy/70">Urutkan</label>
          <div class="mt-1 flex gap-2">
            <select
              v-model="filters.sort_by"
              class="w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
              @change="onSortChange"
            >
              <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
            <button
              type="button"
              class="shrink-0 rounded-md border border-banten-navy/20 px-3 py-2 text-xs font-semibold text-banten-navy hover:bg-banten-sand/50"
              :title="filters.sort_dir === 'asc' ? 'Naik (A→Z)' : 'Turun (Z→A)'"
              @click="toggleSortDir"
            >
              {{ filters.sort_dir === 'asc' ? '↑ Asc' : '↓ Desc' }}
            </button>
          </div>
        </div>
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button type="submit" class="rounded-md bg-banten-navy px-4 py-2 text-sm text-white">Cari</button>
        <button type="button" class="rounded-md border border-banten-navy/20 px-4 py-2 text-sm text-banten-navy" @click="resetFilters">
          Reset
        </button>
      </div>
    </form>

    <form
      v-if="showForm && isAdmin"
      class="mb-6 rounded-xl border border-banten-navy/10 bg-white/90 p-5"
      @submit.prevent="save"
    >
      <h2 class="font-display text-lg text-banten-navy">
        {{ editingId ? 'Edit User' : 'User Baru' }}
      </h2>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div v-if="!editingId">
          <label class="text-sm font-medium text-banten-navy">Username</label>
          <input
            v-model="form.username"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Nama lengkap</label>
          <input
            v-model="form.full_name"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">No. HP</label>
          <input
            v-model="form.phone"
            type="tel"
            inputmode="tel"
            placeholder="08xxxxxxxxxx"
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">
            Password{{ editingId ? ' (opsional)' : '' }}
          </label>
          <div class="relative mt-1">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              :required="!editingId"
              minlength="6"
              class="w-full rounded-md border border-banten-navy/20 py-2 pl-3 pr-10 text-sm outline-none focus:border-banten-gold"
              :placeholder="editingId ? 'Kosongkan jika tidak diubah' : ''"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 flex items-center px-3 text-banten-navy/45 transition hover:text-banten-navy"
              :aria-label="showPassword ? 'Sembunyikan password' : 'Tampilkan password'"
              @click="showPassword = !showPassword"
            >
              <svg
                v-if="!showPassword"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.75"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
                />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
              <svg
                v-else
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.75"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"
                />
              </svg>
            </button>
          </div>
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">Role</label>
          <select
            v-model="form.role_code"
            required
            class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 text-sm"
          >
            <option v-for="r in roles" :key="r.id" :value="r.code">{{ r.name }} ({{ r.code }})</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-banten-navy">
            OPD{{ needsOpd ? ' (wajib)' : ' (opsional)' }}
          </label>
          <SearchableSelect
            v-model="form.opd_id"
            tone="dark"
            :options="opdOptions"
            placeholder="— pilih OPD —"
            search-placeholder="Cari OPD..."
            :required="needsOpd"
          />
        </div>
        <div v-if="editingId" class="flex items-center gap-2 pt-6">
          <input id="is_active" v-model="form.is_active" type="checkbox" class="rounded border-banten-navy/30" />
          <label for="is_active" class="text-sm text-banten-navy">Aktif</label>
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

    <div v-if="loading" class="text-sm text-banten-navy/60">Memuat pengguna...</div>
    <div v-else-if="error" class="rounded-md border border-banten-red/30 bg-red-50 px-4 py-3 text-sm text-banten-red">
      {{ error }}
    </div>
    <div v-else class="overflow-x-auto rounded-xl border border-banten-navy/10 bg-white/90">
      <table class="min-w-full text-left text-sm">
        <thead class="border-b border-banten-navy/10 bg-banten-sand/40 text-xs uppercase tracking-wide text-banten-navy/60">
          <tr>
            <th class="px-4 py-3 font-medium">User</th>
            <th class="px-4 py-3 font-medium">No. HP</th>
            <th class="px-4 py-3 font-medium">Role</th>
            <th class="px-4 py-3 font-medium">OPD</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in users"
            :key="u.id"
            class="border-b border-banten-navy/5 last:border-0"
          >
            <td class="px-4 py-3">
              <p class="font-medium text-banten-navy">{{ u.full_name }}</p>
              <p class="text-xs text-banten-navy/50">@{{ u.username }} · {{ u.email }}</p>
            </td>
            <td class="px-4 py-3 text-banten-navy/70">{{ u.phone || '—' }}</td>
            <td class="px-4 py-3">
              <span class="rounded bg-banten-navy/8 px-2 py-0.5 text-xs font-medium text-banten-navy">
                {{ u.role?.name || '—' }}
              </span>
            </td>
            <td class="px-4 py-3 text-banten-navy/70">{{ u.opd_name || '—' }}</td>
            <td class="px-4 py-3">
              <span
                class="rounded px-2 py-0.5 text-xs font-semibold"
                :class="u.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-600'"
              >
                {{ u.is_active ? 'Aktif' : 'Nonaktif' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <div class="flex justify-end gap-3 text-xs">
                <button type="button" class="text-banten-gold hover:underline" @click="editUser(u)">
                  Edit
                </button>
                <button
                  v-if="u.id !== auth.user?.id"
                  type="button"
                  class="text-banten-red hover:underline"
                  @click="toggleActive(u)"
                >
                  {{ u.is_active ? 'Nonaktifkan' : 'Aktifkan' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <PaginationBar v-if="!loading && !error" :meta="meta" @update:page="onPage" />
  </div>
</template>
