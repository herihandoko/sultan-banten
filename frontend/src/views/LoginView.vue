<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { APP_NAME, APP_VERSION_LABEL } from '../config/app'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('admin')
const password = ref('admin123')

async function onSubmit() {
  const ok = await auth.login(username.value, password.value)
  if (ok) {
    router.push(route.query.redirect || '/')
  }
}
</script>

<template>
  <div class="relative flex min-h-screen flex-col items-center justify-center px-4 pb-16 pt-8">
    <div
      class="pointer-events-none absolute inset-0 opacity-40"
      style="
        background-image:
          linear-gradient(rgba(27, 58, 92, 0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(27, 58, 92, 0.05) 1px, transparent 1px);
        background-size: 32px 32px;
      "
    />

    <div class="relative w-full max-w-md">
      <div class="mb-6 text-center">
        <img
          src="/logo.png"
          alt="Sultan Banten"
          class="mx-auto h-auto w-28 select-none"
        />
        <p class="mt-3 text-sm text-banten-navy/70">
          Sistem Utama Layanan Tanggap Informasi, Manajemen Opini, dan Branding Digital Terpadu
        </p>
      </div>

      <form
        class="rounded-xl border border-banten-navy/10 bg-white/90 p-6 shadow-sm backdrop-blur"
        @submit.prevent="onSubmit"
      >
        <label class="block text-sm font-medium text-banten-navy">Username</label>
        <input
          v-model="username"
          type="text"
          autocomplete="username"
          class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 outline-none focus:border-banten-gold"
          required
        />

        <label class="mt-4 block text-sm font-medium text-banten-navy">Password</label>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          class="mt-1 w-full rounded-md border border-banten-navy/20 px-3 py-2 outline-none focus:border-banten-gold"
          required
        />

        <p v-if="auth.error" class="mt-3 text-sm text-banten-red">{{ auth.error }}</p>

        <button
          type="submit"
          class="mt-6 w-full rounded-md bg-banten-navy px-4 py-2.5 text-sm font-medium text-white transition hover:bg-banten-navy-dark disabled:opacity-60"
          :disabled="auth.loading"
        >
          {{ auth.loading ? 'Masuk...' : 'Masuk' }}
        </button>

        <p class="mt-4 text-center text-xs text-banten-navy/50">
          Demo: admin / admin123
        </p>
      </form>
    </div>

    <footer class="absolute inset-x-0 bottom-0 py-4 text-center text-xs text-banten-navy/45">
      {{ APP_NAME }} · {{ APP_VERSION_LABEL }}
    </footer>
  </div>
</template>
