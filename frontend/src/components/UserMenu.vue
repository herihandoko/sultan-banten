<script setup>
import { computed, ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const open = ref(false)
const rootEl = ref(null)
const panel = ref('')
const fileEl = ref(null)

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const preview = ref('')
const busy = ref(false)
const message = ref('')
const error = ref('')

onClickOutside(rootEl, () => {
  if (!panel.value) open.value = false
})

const displayName = computed(() => auth.user?.full_name || auth.user?.username || 'User')
const roleName = computed(() => auth.user?.role?.name || '—')
const avatar = computed(() => auth.user?.avatar || '')

const initials = computed(() => {
  const name = displayName.value.trim()
  const parts = name.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase() || 'U'
})

function resetForm() {
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  preview.value = avatar.value
  message.value = ''
  error.value = ''
}

function openPanel(name) {
  open.value = false
  panel.value = name
  resetForm()
}

function closePanel() {
  panel.value = ''
  resetForm()
}

async function onLogout() {
  open.value = false
  await auth.logout()
  window.location.assign('/login')
}

function readPhoto(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    error.value = 'Pilih foto JPEG, PNG, atau WebP'
    return
  }
  error.value = ''
  const reader = new FileReader()
  reader.onload = () => {
    const img = new Image()
    img.onload = () => {
      const size = 256
      const canvas = document.createElement('canvas')
      canvas.width = size
      canvas.height = size
      const ctx = canvas.getContext('2d')
      const scale = Math.max(size / img.width, size / img.height)
      const w = img.width * scale
      const h = img.height * scale
      ctx.drawImage(img, (size - w) / 2, (size - h) / 2, w, h)
      preview.value = canvas.toDataURL('image/jpeg', 0.82)
    }
    img.src = reader.result
  }
  reader.readAsDataURL(file)
}

async function savePhoto() {
  busy.value = true
  error.value = ''
  message.value = ''
  try {
    await auth.updateProfile({ avatar: preview.value || null })
    message.value = preview.value ? 'Foto profil disimpan.' : 'Foto profil dihapus.'
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal menyimpan foto'
  } finally {
    busy.value = false
  }
}

async function savePassword() {
  error.value = ''
  message.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Konfirmasi password tidak sama'
    return
  }
  busy.value = true
  try {
    await auth.updateProfile({
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    message.value = 'Password berhasil diganti.'
  } catch (err) {
    error.value = err.response?.data?.error || 'Gagal mengganti password'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div ref="rootEl" class="relative">
    <button
      type="button"
      class="flex max-w-[11rem] items-center gap-2 rounded-lg border border-[#30363d] bg-[#161b22] p-1 text-left transition hover:border-emerald-500/40 sm:max-w-[16rem] sm:px-2.5 sm:py-1"
      :aria-expanded="open"
      aria-haspopup="menu"
      @click="open = !open"
    >
      <span
        class="flex h-7 w-7 shrink-0 items-center justify-center overflow-hidden rounded-md bg-emerald-500/20 text-[11px] font-bold tracking-wide text-emerald-300"
        aria-hidden="true"
      >
        <img v-if="avatar" :src="avatar" alt="" class="h-full w-full object-cover" />
        <template v-else>{{ initials }}</template>
      </span>
      <span class="hidden min-w-0 flex-1 sm:block">
        <span class="block truncate text-xs font-semibold leading-tight text-white">
          {{ displayName }}
        </span>
        <span class="block truncate text-[10px] leading-tight text-[#8b949e]">
          {{ roleName }}
        </span>
      </span>
      <svg
        class="hidden h-3.5 w-3.5 shrink-0 text-[#8b949e] sm:block"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6" />
      </svg>
    </button>

    <div
      v-if="open"
      class="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-xl border border-[#30363d] bg-[#161b22] py-1 shadow-2xl"
      role="menu"
    >
      <div class="border-b border-[#30363d] px-3 py-2.5 sm:hidden">
        <p class="truncate text-xs font-semibold text-white">{{ displayName }}</p>
        <p class="truncate text-[10px] text-[#8b949e]">{{ roleName }}</p>
      </div>
      <button
        type="button"
        role="menuitem"
        class="flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-semibold text-[#c9d1d9] transition hover:bg-[#21262d] hover:text-white"
        @click="openPanel('photo')"
      >
        <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 8.69 5.25h6.62a2.31 2.31 0 0 1 1.863.925l.773 1.15A1.15 1.15 0 0 0 18.9 8h.85A2.25 2.25 0 0 1 22 10.25v7.5A2.25 2.25 0 0 1 19.75 20H4.25A2.25 2.25 0 0 1 2 17.75v-7.5A2.25 2.25 0 0 1 4.25 8h.85a1.15 1.15 0 0 0 .954-.675l.773-1.15ZM12 16.5a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z" />
        </svg>
        Foto profil
      </button>
      <button
        type="button"
        role="menuitem"
        class="flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-semibold text-[#c9d1d9] transition hover:bg-[#21262d] hover:text-white"
        @click="openPanel('password')"
      >
        <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V7.875a4.5 4.5 0 1 0-9 0V10.5m-.75 0h10.5A1.5 1.5 0 0 1 18.75 12v6.75a1.5 1.5 0 0 1-1.5 1.5H6.75a1.5 1.5 0 0 1-1.5-1.5V12a1.5 1.5 0 0 1 1.5-1.5Z" />
        </svg>
        Ganti password
      </button>
      <button
        type="button"
        role="menuitem"
        class="flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-semibold text-[#c9d1d9] transition hover:bg-[#21262d] hover:text-rose-400"
        @click="onLogout"
      >
        <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6A2.25 2.25 0 0 0 5.25 5.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l3 3m0 0-3 3m3-3H9" />
        </svg>
        Keluar
      </button>
    </div>

    <div
      v-if="panel"
      class="fixed inset-0 z-[80] flex items-center justify-center bg-black/60 p-4"
      @click.self="closePanel"
    >
      <form
        class="w-full max-w-sm rounded-2xl border border-[#30363d] bg-[#161b22] p-5 shadow-2xl"
        @submit.prevent="panel === 'password' ? savePassword() : savePhoto()"
      >
        <h2 class="text-sm font-semibold text-white">
          {{ panel === 'password' ? 'Ganti password' : 'Foto profil' }}
        </h2>

        <div v-if="panel === 'photo'" class="mt-4 space-y-4">
          <div class="flex items-center gap-4">
            <span class="flex h-16 w-16 items-center justify-center overflow-hidden rounded-2xl bg-emerald-500/20 text-sm font-bold text-emerald-300">
              <img v-if="preview" :src="preview" alt="" class="h-full w-full object-cover" />
              <template v-else>{{ initials }}</template>
            </span>
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-white">{{ displayName }}</p>
              <p class="text-[11px] text-[#8b949e]">JPEG, PNG, atau WebP. Foto dipotong persegi.</p>
            </div>
          </div>
          <input ref="fileEl" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="readPhoto" />
          <div class="flex gap-2">
            <button
              type="button"
              class="rounded-xl border border-[#30363d] px-3 py-2 text-xs font-semibold text-[#c9d1d9] hover:bg-[#21262d]"
              @click="fileEl?.click()"
            >
              Pilih foto
            </button>
            <button
              v-if="preview"
              type="button"
              class="rounded-xl border border-[#30363d] px-3 py-2 text-xs font-semibold text-rose-300 hover:bg-[#21262d]"
              @click="preview = ''"
            >
              Hapus
            </button>
          </div>
        </div>

        <div v-else class="mt-4 space-y-3">
          <label class="block text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">
            Password saat ini
            <input v-model="currentPassword" type="password" autocomplete="current-password" required class="mt-1 w-full rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm font-normal normal-case tracking-normal text-[#e6edf3] outline-none focus:border-emerald-500/60" />
          </label>
          <label class="block text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">
            Password baru
            <input v-model="newPassword" type="password" autocomplete="new-password" minlength="8" required class="mt-1 w-full rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm font-normal normal-case tracking-normal text-[#e6edf3] outline-none focus:border-emerald-500/60" />
          </label>
          <label class="block text-[11px] font-semibold uppercase tracking-wide text-[#8b949e]">
            Ulangi password baru
            <input v-model="confirmPassword" type="password" autocomplete="new-password" minlength="8" required class="mt-1 w-full rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2 text-sm font-normal normal-case tracking-normal text-[#e6edf3] outline-none focus:border-emerald-500/60" />
          </label>
        </div>

        <p v-if="error" class="mt-3 text-xs text-rose-300">{{ error }}</p>
        <p v-if="message" class="mt-3 text-xs text-emerald-300">{{ message }}</p>

        <div class="mt-5 flex justify-end gap-2">
          <button type="button" class="rounded-xl px-3 py-2 text-xs font-semibold text-[#8b949e] hover:text-white" @click="closePanel">
            Tutup
          </button>
          <button
            type="submit"
            class="rounded-xl bg-emerald-500 px-3 py-2 text-xs font-semibold text-[#042f1b] hover:bg-emerald-400 disabled:opacity-60"
            :disabled="busy"
          >
            {{ busy ? 'Menyimpan…' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
