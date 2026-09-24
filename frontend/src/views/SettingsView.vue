<script setup>
import { onMounted, ref, watch } from 'vue'
import api from '../services/api'
import { useNewsSourceStore } from '../stores/newsSource'

const store = useNewsSourceStore()
const tab = ref('source')
const draft = ref(store.newsSource)
const ok = ref('')

const wa = ref({
  token: '',
  token_set: false,
  country_code: '62',
  crisis_number: '',
})
const mail = ref({
  enabled: false,
  host: '',
  port: 587,
  username: '',
  password: '',
  password_set: false,
  encryption: 'tls',
  from_address: '',
  from_name: 'SIAGAPIM Banten',
})
const channelError = ref('')
const channelOk = ref('')
const savingChannel = ref(false)

const inputClass =
  'mt-1 w-full rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm text-[#e6edf3] placeholder:text-[#6e7681] outline-none transition focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30'

const tabs = [
  { id: 'source', label: 'Sumber berita' },
  { id: 'whatsapp', label: 'WhatsApp' },
  { id: 'email', label: 'Email' },
]

onMounted(async () => {
  await store.load()
  draft.value = store.newsSource
  await loadMessaging()
})

watch(
  () => store.newsSource,
  (value) => {
    draft.value = value
  },
)

function applyMessaging(data) {
  const whatsapp = data?.whatsapp || {}
  const email = data?.email || {}
  wa.value = {
    token: '',
    token_set: Boolean(whatsapp.token_set),
    country_code: whatsapp.country_code || '62',
    crisis_number: whatsapp.crisis_number || '',
  }
  mail.value = {
    enabled: Boolean(email.enabled),
    host: email.host || '',
    port: email.port || 587,
    username: email.username || '',
    password: '',
    password_set: Boolean(email.password_set),
    encryption: email.encryption || 'tls',
    from_address: email.from_address || '',
    from_name: email.from_name || 'SIAGAPIM Banten',
  }
}

async function loadMessaging() {
  channelError.value = ''
  try {
    const { data } = await api.get('/settings/messaging')
    applyMessaging(data.data)
  } catch (err) {
    channelError.value = err.response?.data?.error || 'Gagal memuat pengaturan kanal'
  }
}

async function saveSource() {
  ok.value = ''
  const success = await store.setSource(draft.value)
  if (success) ok.value = 'Sumber berita disimpan.'
}

async function saveWhatsapp() {
  savingChannel.value = true
  channelError.value = ''
  channelOk.value = ''
  try {
    const payload = {
      whatsapp: {
        country_code: wa.value.country_code,
        crisis_number: wa.value.crisis_number,
      },
    }
    if (wa.value.token.trim()) payload.whatsapp.token = wa.value.token.trim()
    const { data } = await api.put('/settings/messaging', payload)
    applyMessaging(data.data)
    channelOk.value = 'Pengaturan WhatsApp disimpan.'
  } catch (err) {
    channelError.value = err.response?.data?.error || 'Gagal menyimpan WhatsApp'
  } finally {
    savingChannel.value = false
  }
}

async function saveEmail() {
  savingChannel.value = true
  channelError.value = ''
  channelOk.value = ''
  try {
    const payload = {
      email: {
        enabled: mail.value.enabled,
        host: mail.value.host,
        port: Number(mail.value.port) || 587,
        username: mail.value.username,
        encryption: mail.value.encryption,
        from_address: mail.value.from_address,
        from_name: mail.value.from_name,
      },
    }
    if (mail.value.password.trim()) payload.email.password = mail.value.password
    const { data } = await api.put('/settings/messaging', payload)
    applyMessaging(data.data)
    channelOk.value = 'Pengaturan email disimpan.'
  } catch (err) {
    channelError.value = err.response?.data?.error || 'Gagal menyimpan email'
  } finally {
    savingChannel.value = false
  }
}

function selectTab(id) {
  tab.value = id
  ok.value = ''
  channelOk.value = ''
  channelError.value = ''
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <div>
      <h1 class="text-2xl font-bold tracking-tight text-white">Pengaturan</h1>
      <p class="mt-1 text-sm text-[#8b949e]">
        Sumber monitoring, WhatsApp, dan email yang dipakai SIAGAPIM.
      </p>
    </div>

    <div class="flex gap-1 rounded-xl border border-[#30363d] bg-[#161b22] p-1">
      <button
        v-for="item in tabs"
        :key="item.id"
        type="button"
        class="flex-1 rounded-lg px-3 py-2 text-sm font-medium transition"
        :class="
          tab === item.id
            ? 'bg-emerald-500 text-black'
            : 'text-[#8b949e] hover:bg-[#21262d] hover:text-white'
        "
        @click="selectTab(item.id)"
      >
        {{ item.label }}
      </button>
    </div>

    <section v-if="tab === 'source'" class="rounded-2xl border border-[#30363d] bg-[#161b22] p-5 space-y-4">
      <h2 class="text-sm font-semibold text-white">Sumber berita / listening</h2>

      <label
        class="flex cursor-pointer gap-3 rounded-xl border px-4 py-3 transition"
        :class="
          draft === 'sipantau'
            ? 'border-emerald-500/50 bg-emerald-500/10'
            : 'border-[#30363d] hover:border-[#484f58]'
        "
      >
        <input v-model="draft" type="radio" value="sipantau" class="mt-1" />
        <span>
          <span class="block text-sm font-semibold text-[#e6edf3]">SIPANTAU</span>
          <span class="mt-0.5 block text-[11px] text-[#8b949e]">
            Listening internal · link SIPANTAU di header · sync semua isu negatif ke Crisis Room.
          </span>
        </span>
      </label>

      <label
        class="flex cursor-pointer gap-3 rounded-xl border px-4 py-3 transition"
        :class="
          draft === 'mata_bathin'
            ? 'border-emerald-500/50 bg-emerald-500/10'
            : 'border-[#30363d] hover:border-[#484f58]'
        "
      >
        <input v-model="draft" type="radio" value="mata_bathin" class="mt-1" />
        <span>
          <span class="block text-sm font-semibold text-[#e6edf3]">Mata Bathin</span>
          <span class="mt-0.5 block text-[11px] text-[#8b949e]">
            Sumber eksternal Mata Bathin · sembunyikan link SIPANTAU · sync SIPANTAU dimatikan.
          </span>
        </span>
      </label>

      <p v-if="store.error" class="text-xs text-rose-400">{{ store.error }}</p>
      <p v-if="ok" class="text-xs text-emerald-400">{{ ok }}</p>

      <div class="flex justify-end pt-1">
        <button
          type="button"
          class="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-60"
          :disabled="store.saving || draft === store.newsSource"
          @click="saveSource"
        >
          {{ store.saving ? 'Menyimpan…' : 'Simpan' }}
        </button>
      </div>
    </section>

    <section v-else-if="tab === 'whatsapp'" class="space-y-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
      <div>
        <h2 class="text-sm font-semibold text-white">WhatsApp (Fonnte)</h2>
        <p class="mt-1 text-[11px] text-[#8b949e]">
          Dipakai untuk blast Media Hub dan notifikasi krisis. Token yang sudah tersimpan tidak
          ditampilkan ulang.
        </p>
      </div>

      <label class="block text-xs text-[#8b949e]">
        Token Fonnte
        <input
          v-model="wa.token"
          type="password"
          autocomplete="new-password"
          :class="inputClass"
          :placeholder="wa.token_set ? 'Token sudah tersimpan — isi hanya jika diganti' : 'Tempel token dari Fonnte'"
        />
      </label>
      <p v-if="wa.token_set" class="text-[11px] text-emerald-400">Token aktif.</p>

      <div class="grid gap-3 sm:grid-cols-2">
        <label class="block text-xs text-[#8b949e]">
          Kode negara
          <input v-model="wa.country_code" :class="inputClass" placeholder="62" />
        </label>
        <label class="block text-xs text-[#8b949e]">
          Nomor WhatsApp krisis
          <input v-model="wa.crisis_number" :class="inputClass" placeholder="62812xxxxxxx" />
        </label>
      </div>

      <p v-if="channelError" class="text-xs text-rose-400">{{ channelError }}</p>
      <p v-if="channelOk" class="text-xs text-emerald-400">{{ channelOk }}</p>

      <div class="flex justify-end pt-1">
        <button
          type="button"
          class="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-60"
          :disabled="savingChannel"
          @click="saveWhatsapp"
        >
          {{ savingChannel ? 'Menyimpan…' : 'Simpan' }}
        </button>
      </div>
    </section>

    <section v-else class="space-y-4 rounded-2xl border border-[#30363d] bg-[#161b22] p-5">
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-sm font-semibold text-white">Email SMTP</h2>
          <p class="mt-1 text-[11px] text-[#8b949e]">Dipakai untuk blast Media Hub dan email uji.</p>
        </div>
        <label class="inline-flex items-center gap-2 text-xs text-[#c9d1d9]">
          <input v-model="mail.enabled" type="checkbox" class="accent-emerald-500" />
          Aktif
        </label>
      </div>

      <div class="grid gap-3 sm:grid-cols-3">
        <label class="block text-xs text-[#8b949e] sm:col-span-2">
          Host
          <input v-model="mail.host" :class="inputClass" placeholder="smtp.example.com" />
        </label>
        <label class="block text-xs text-[#8b949e]">
          Port
          <input v-model.number="mail.port" type="number" min="1" max="65535" :class="inputClass" />
        </label>
      </div>

      <label class="block text-xs text-[#8b949e]">
        Enkripsi
        <select v-model="mail.encryption" :class="inputClass">
          <option value="tls">TLS</option>
          <option value="ssl">SSL</option>
          <option value="none">Tanpa enkripsi</option>
        </select>
      </label>

      <div class="grid gap-3 sm:grid-cols-2">
        <label class="block text-xs text-[#8b949e]">
          Username
          <input v-model="mail.username" :class="inputClass" autocomplete="off" />
        </label>
        <label class="block text-xs text-[#8b949e]">
          Password
          <input
            v-model="mail.password"
            type="password"
            autocomplete="new-password"
            :class="inputClass"
            :placeholder="mail.password_set ? 'Password sudah tersimpan — isi hanya jika diganti' : 'Password SMTP'"
          />
        </label>
      </div>
      <p v-if="mail.password_set" class="text-[11px] text-emerald-400">Password SMTP tersimpan.</p>

      <div class="grid gap-3 sm:grid-cols-2">
        <label class="block text-xs text-[#8b949e]">
          Alamat pengirim
          <input v-model="mail.from_address" type="email" :class="inputClass" placeholder="no-reply@bantenprov.go.id" />
        </label>
        <label class="block text-xs text-[#8b949e]">
          Nama pengirim
          <input v-model="mail.from_name" :class="inputClass" />
        </label>
      </div>

      <p v-if="channelError" class="text-xs text-rose-400">{{ channelError }}</p>
      <p v-if="channelOk" class="text-xs text-emerald-400">{{ channelOk }}</p>

      <div class="flex justify-end pt-1">
        <button
          type="button"
          class="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-60"
          :disabled="savingChannel"
          @click="saveEmail"
        >
          {{ savingChannel ? 'Menyimpan…' : 'Simpan' }}
        </button>
      </div>
    </section>
  </div>
</template>
