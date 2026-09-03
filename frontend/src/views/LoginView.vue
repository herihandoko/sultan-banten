<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { APP_NAME, APP_FULL_NAME, APP_VERSION_LABEL } from '../config/app'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')

async function onSubmit() {
  const ok = await auth.login(username.value, password.value)
  if (ok) {
    router.push('/')
  }
}
</script>

<template>
  <div class="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-4 pb-16 pt-8">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center bg-no-repeat"
      style="background-image: url('/siagapim_login.png')"
      aria-hidden="true"
    />
    <div
      class="pointer-events-none absolute inset-0 bg-gradient-to-b from-white/55 via-white/25 to-banten-navy/35"
      aria-hidden="true"
    />

    <div class="relative w-full max-w-md">
      <div class="mb-6 text-center">
        <img
          src="/pavicon.png"
          :alt="APP_NAME"
          class="mx-auto h-auto w-24 select-none drop-shadow-sm"
        />
        <h1 class="mt-4 font-display text-2xl tracking-wide text-banten-navy drop-shadow-sm">
          {{ APP_NAME }}
        </h1>
        <p class="mt-1 text-sm font-medium text-banten-navy/85">{{ APP_FULL_NAME }}</p>
      </div>

      <form
        class="rounded-xl border border-banten-navy/10 bg-white/95 p-6 shadow-lg backdrop-blur-sm"
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
      </form>
    </div>

    <footer class="absolute inset-x-0 bottom-0 py-4 text-center text-xs text-white/80">
      {{ APP_NAME }} · {{ APP_VERSION_LABEL }}
    </footer>
  </div>
</template>
