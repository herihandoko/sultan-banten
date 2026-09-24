<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { APP_FULL_NAME, APP_NAME, APP_VERSION_LABEL } from '../config/app'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const showPassword = ref(false)

function safeNextPath() {
  const raw = typeof route.query.next === 'string' ? route.query.next : ''
  if (raw.startsWith('/') && !raw.startsWith('//')) return raw
  return '/'
}

async function onSubmit() {
  const ok = await auth.login(username.value, password.value)
  if (ok) {
    const next = safeNextPath()
    if (next.startsWith('/sipantau') || next.startsWith('/panten')) {
      window.location.assign(next)
      return
    }
    router.push(next)
  }
}
</script>

<template>
  <div class="login-page relative flex min-h-dvh items-center justify-center overflow-hidden px-4 py-10">
    <div
      class="pointer-events-none absolute inset-0 scale-105 bg-cover bg-center bg-no-repeat"
      style="background-image: url('/siagapim_login.png')"
      aria-hidden="true"
    />
    <div class="login-photo-overlay pointer-events-none absolute inset-0" aria-hidden="true" />
    <div
      class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(13,17,23,0.55)_78%)]"
      aria-hidden="true"
    />

    <div class="relative w-full max-w-[420px]">
      <section
        class="login-panel rounded-[28px] border p-7 shadow-2xl backdrop-blur-xl sm:p-8"
        :class="
          theme.isDark
            ? 'border-white/10 bg-[#161b22]/80 shadow-black/40'
            : 'border-white/70 bg-white/80 shadow-banten-navy/20'
        "
      >
        <div class="text-center">
          <img
            src="/pavicon.png"
            :alt="APP_NAME"
            class="mx-auto h-28 w-auto select-none object-contain drop-shadow-[0_10px_18px_rgba(0,0,0,0.35)]"
          />
          <p
            class="mt-5 text-[11px] font-semibold uppercase tracking-[0.22em]"
            :class="theme.isDark ? 'text-emerald-300/80' : 'text-banten-navy/70'"
          >
            Biro Adpim Setda Provinsi Banten
          </p>
          <h1
            class="login-brand-title mt-3 font-sans text-[1.95rem] font-medium leading-none tracking-[-0.04em]"
          >
            <span :class="theme.isDark ? 'text-white' : 'text-banten-navy'">Siagapim</span>
            <span
              class="font-semibold"
              :class="theme.isDark ? 'text-emerald-200' : 'text-emerald-700'"
            >
              Banten</span>
          </h1>
          <p
            class="login-brand-sub mx-auto mt-2 max-w-[18rem] text-sm leading-relaxed"
            :class="theme.isDark ? 'text-[#8b949e]' : 'text-banten-navy/75'"
          >
            {{ APP_FULL_NAME }}
          </p>
        </div>

        <form class="mt-7 space-y-4" @submit.prevent="onSubmit">
          <label class="block">
            <span
              class="mb-1.5 block text-xs font-semibold uppercase tracking-wide"
              :class="theme.isDark ? 'text-[#8b949e]' : 'text-banten-navy/70'"
            >
              Username
            </span>
            <span class="relative block">
              <svg
                class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2"
                :class="theme.isDark ? 'text-[#6e7681]' : 'text-banten-navy/40'"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.75"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15.75 6.75a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 19.25a7.5 7.5 0 0 1 15 0"
                />
              </svg>
              <input
                v-model="username"
                type="text"
                autocomplete="username"
                placeholder="Nama pengguna"
                class="login-input w-full rounded-2xl border py-3 pl-11 pr-4 text-sm outline-none transition"
                :class="
                  theme.isDark
                    ? 'border-[#30363d] bg-[#0d1117]/90 text-[#e6edf3] placeholder:text-[#6e7681] focus:border-emerald-400/70 focus:ring-4 focus:ring-emerald-500/15'
                    : 'border-banten-navy/15 bg-white text-banten-navy placeholder:text-banten-navy/35 focus:border-banten-gold focus:ring-4 focus:ring-banten-gold/20'
                "
                required
              />
            </span>
          </label>

          <label class="block">
            <span
              class="mb-1.5 block text-xs font-semibold uppercase tracking-wide"
              :class="theme.isDark ? 'text-[#8b949e]' : 'text-banten-navy/70'"
            >
              Password
            </span>
            <span class="relative block">
              <svg
                class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2"
                :class="theme.isDark ? 'text-[#6e7681]' : 'text-banten-navy/40'"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.75"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M16.5 10.5V7.875a4.5 4.5 0 1 0-9 0V10.5m-.75 0h10.5A1.5 1.5 0 0 1 18.75 12v6.75a1.5 1.5 0 0 1-1.5 1.5H6.75a1.5 1.5 0 0 1-1.5-1.5V12a1.5 1.5 0 0 1 1.5-1.5Z"
                />
              </svg>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="Kata sandi"
                class="login-input w-full rounded-2xl border py-3 pl-11 pr-12 text-sm outline-none transition"
                :class="
                  theme.isDark
                    ? 'border-[#30363d] bg-[#0d1117]/90 text-[#e6edf3] placeholder:text-[#6e7681] focus:border-emerald-400/70 focus:ring-4 focus:ring-emerald-500/15'
                    : 'border-banten-navy/15 bg-white text-banten-navy placeholder:text-banten-navy/35 focus:border-banten-gold focus:ring-4 focus:ring-banten-gold/20'
                "
                required
              />
              <button
                type="button"
                class="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl px-2 py-1 text-[11px] font-semibold"
                :class="theme.isDark ? 'text-[#8b949e] hover:text-white' : 'text-banten-navy/60 hover:text-banten-navy'"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? 'Sembunyi' : 'Lihat' }}
              </button>
            </span>
          </label>

          <p
            v-if="auth.error"
            class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300"
          >
            {{ auth.error }}
          </p>

          <button
            type="submit"
            class="mt-1 flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-[#042f1b] shadow-lg shadow-emerald-950/30 transition hover:bg-emerald-400 disabled:cursor-wait disabled:opacity-70"
            :disabled="auth.loading"
          >
            <svg
              v-if="auth.loading"
              class="h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <circle class="opacity-25" cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" />
              <path class="opacity-90" fill="currentColor" d="M21 12a9 9 0 0 0-9-9v3a6 6 0 0 1 6 6h3Z" />
            </svg>
            {{ auth.loading ? 'Memeriksa akun…' : 'Masuk' }}
          </button>
        </form>
      </section>

      <p
        class="mt-5 text-center text-[11px] tracking-wide text-white/75"
      >
        {{ APP_NAME }} · {{ APP_VERSION_LABEL }}
      </p>
    </div>
  </div>
</template>
