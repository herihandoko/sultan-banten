<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useLocalStorage } from '@vueuse/core'
import { APP_NAME, APP_VERSION_LABEL } from '../config/app'
import { useAuthStore } from '../stores/auth'
import AlertBell from '../components/AlertBell.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const collapsed = useLocalStorage('sb-sidebar-collapsed', false)
const mobileOpen = ref(false)

const nav = computed(() => {
  const role = auth.user?.role?.code
  const items = [
    { to: '/', label: 'Dashboard', match: 'dashboard', icon: 'chart' },
    { to: '/crisis-room', label: 'Crisis Room', match: 'crisis-room', icon: 'radar' },
    { to: '/validasi-opd', label: 'Validasi OPD', match: 'validasi-opd', icon: 'clipboard' },
    { to: '/konten', label: 'Hub Konten', match: 'konten', icon: 'document' },
    { to: '/media-hub', label: 'Media Hub', match: 'media-hub', icon: 'newspaper' },
    { to: '/agenda', label: 'Agenda', match: 'agenda', icon: 'calendar' },
    { to: '/missions', label: 'Mission Board', match: 'missions', icon: 'flag' },
    { to: '/kol', label: 'KOL', match: 'kol', icon: 'megaphone' },
    { to: '/arsip', label: 'Arsip', match: 'arsip', icon: 'archive' },
    { to: '/executive', label: 'Eksekutif', match: 'executive', icon: 'briefcase' },
    { to: '/reports', label: 'Laporan', match: 'reports', icon: 'document' },
    { to: '/opds', label: 'Master OPD', match: 'opds', icon: 'clipboard' },
    { to: '/users', label: 'Users', match: 'users', icon: 'users' },
  ]
  if (role === 'opd_admin') {
    return items.filter((i) => ['dashboard', 'validasi-opd', 'crisis-room'].includes(i.match))
  }
  if (role === 'asn') {
    return items.filter((i) => i.match === 'missions')
  }
  if (role === 'pimpinan') {
    return items.filter((i) =>
      [
        'dashboard',
        'crisis-room',
        'validasi-opd',
        'konten',
        'media-hub',
        'missions',
        'agenda',
        'arsip',
        'executive',
        'reports',
      ].includes(i.match),
    )
  }
  if (role === 'media_kol_admin') {
    return items.filter((i) =>
      ['dashboard', 'media-hub', 'agenda', 'kol', 'arsip', 'reports'].includes(i.match),
    )
  }
  if (role === 'editor') {
    return items.filter((i) =>
      [
        'dashboard',
        'crisis-room',
        'validasi-opd',
        'konten',
        'media-hub',
        'agenda',
        'missions',
        'arsip',
        'reports',
      ].includes(i.match),
    )
  }
  return items
})

const roleName = computed(() => auth.user?.role?.name || '—')
const showAlerts = computed(() =>
  ['super_admin', 'editor', 'pimpinan', 'media_kol_admin'].includes(auth.user?.role?.code),
)

function isActive(item) {
  return (
    route.name === item.match
    || (item.match === 'crisis-room' && route.name === 'issue-detail')
    || (item.match === 'konten' && route.name === 'konten-detail')
  )
}

function toggleSidebar() {
  collapsed.value = !collapsed.value
}

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}

watch(
  () => route.fullPath,
  () => {
    mobileOpen.value = false
  },
)
</script>

<template>
  <div
    class="min-h-screen lg:grid lg:transition-[grid-template-columns] lg:duration-300"
    :class="collapsed ? 'lg:grid-cols-[72px_1fr]' : 'lg:grid-cols-[260px_1fr]'"
  >
    <!-- Mobile overlay -->
    <button
      v-if="mobileOpen"
      type="button"
      class="fixed inset-0 z-30 bg-banten-navy/40 lg:hidden"
      aria-label="Tutup menu"
      @click="mobileOpen = false"
    />

    <aside
      class="z-40 overflow-visible border-white/10 bg-banten-navy text-white transition-all duration-300 max-lg:fixed max-lg:inset-y-0 max-lg:left-0 max-lg:w-[260px] max-lg:shadow-2xl lg:relative lg:min-h-screen lg:border-r"
      :class="[
        mobileOpen ? 'max-lg:translate-x-0' : 'max-lg:-translate-x-full',
        collapsed ? 'lg:w-[72px]' : 'lg:w-auto',
      ]"
    >
      <div class="flex items-start gap-2 px-3 pb-3 pt-4" :class="collapsed ? 'lg:justify-center' : ''">
        <RouterLink
          to="/"
          class="group min-w-0 flex-1 overflow-hidden rounded-xl bg-white shadow-[0_8px_24px_rgba(0,0,0,0.18)] ring-1 ring-white/20 transition hover:shadow-[0_10px_28px_rgba(0,0,0,0.22)]"
          :class="collapsed ? 'lg:w-11 lg:flex-none' : ''"
          :title="collapsed ? 'Sultan Banten' : undefined"
        >
          <div
            class="flex items-center justify-center"
            :class="collapsed ? 'lg:px-1.5 lg:py-2' : 'px-3 pb-2 pt-2.5'"
          >
            <img
              src="/logo.png"
              alt="Sultan Banten"
              class="h-auto select-none transition duration-300 group-hover:scale-[1.03]"
              :class="collapsed ? 'w-8 lg:w-7' : 'w-16'"
            />
          </div>
          <div class="grid h-0.5 grid-cols-3" :class="collapsed ? 'lg:hidden' : ''">
            <span class="bg-[#43A047]" />
            <span class="bg-banten-gold" />
            <span class="bg-[#1E5BB8]" />
          </div>
        </RouterLink>

        <button
          type="button"
          class="rounded-md p-2 text-white/70 hover:bg-white/10 hover:text-white lg:hidden"
          aria-label="Tutup menu"
          @click="mobileOpen = false"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <p
        class="mt-0.5 px-4 text-center text-[11px] leading-snug tracking-wide text-white/55"
        :class="collapsed ? 'lg:hidden' : ''"
      >
        Crisis Response &amp; Media Engagement
      </p>

      <div
        class="mx-3 my-3 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"
        :class="collapsed ? 'lg:mx-2' : ''"
      />

      <nav class="flex flex-col gap-0.5 px-2 pb-4" :class="collapsed ? 'lg:items-center lg:px-1.5' : ''">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="group relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition"
          :class="[
            collapsed ? 'lg:justify-center lg:px-0 lg:w-11' : '',
            isActive(item)
              ? 'bg-white/15 text-banten-gold'
              : 'text-white/80 hover:bg-white/10 hover:text-white',
          ]"
        >
          <span class="inline-flex h-5 w-5 shrink-0 items-center justify-center">
            <!-- radar -->
            <svg v-if="item.icon === 'radar'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 12m-9 0a9 9 0 1 0 18 0 9 9 0 1 0-18 0" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 12m-5 0a5 5 0 1 0 10 0 5 5 0 1 0-10 0" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 12m-1 0a1 1 0 1 0 2 0 1 1 0 1 0-2 0" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.5M19.5 8.5l-1.8 1.2" />
            </svg>
            <!-- clipboard -->
            <svg v-else-if="item.icon === 'clipboard'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5h6a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2M9 12l2 2 4-4" />
            </svg>
            <!-- document -->
            <svg v-else-if="item.icon === 'document'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M14 3v5h5M9 13h6M9 17h4" />
            </svg>
            <!-- newspaper -->
            <svg v-else-if="item.icon === 'newspaper'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 5h12a2 2 0 0 1 2 2v12H6a2 2 0 0 1-2-2V5Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M18 9h2a1 1 0 0 1 1 1v7a2 2 0 0 1-2 2h-1M8 9h6M8 13h6M8 17h3" />
            </svg>
            <!-- calendar -->
            <svg v-else-if="item.icon === 'calendar'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 4v2M17 4v2M4 9h16M6 6h12a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 13h2v2H8zM12 13h2v2h-2z" />
            </svg>
            <!-- flag -->
            <svg v-else-if="item.icon === 'flag'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 21V4m0 0h9l-1.5 3.5L14 11H5" />
            </svg>
            <!-- megaphone -->
            <svg v-else-if="item.icon === 'megaphone'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 5.5 19 3v14l-8-2.5V5.5Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 14.5v3.2a1.8 1.8 0 0 1-3.5.6L7 14.5M19 8.5v5" />
            </svg>
            <!-- archive -->
            <svg v-else-if="item.icon === 'archive'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16v2H4V7Zm1 2v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9M10 13h4M4 5h16v2H4V5Z" />
            </svg>
            <!-- chart -->
            <svg v-else-if="item.icon === 'chart'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 19V5M4 19h16M8 16v-5M12 16V8M16 16v-3" />
            </svg>
            <!-- briefcase -->
            <svg v-else-if="item.icon === 'briefcase'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 6V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1M4 10h16v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8ZM4 10l1.2-2.4A2 2 0 0 1 7 6.5h10a2 2 0 0 1 1.8 1.1L20 10" />
            </svg>
            <!-- users -->
            <svg v-else-if="item.icon === 'users'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 19v-1a3 3 0 0 0-3-3H7a3 3 0 0 0-3 3v1" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM19 19v-1a3 3 0 0 0-2-2.83M15.5 6.17a3 3 0 0 1 0 5.66" />
            </svg>
          </span>
          <span
            class="truncate"
            :class="collapsed ? 'lg:sr-only' : ''"
          >
            {{ item.label }}
          </span>
          <!-- Tooltip saat sidebar collapsed -->
          <span
            v-if="collapsed"
            class="pointer-events-none absolute top-1/2 left-full z-50 ml-3 hidden -translate-y-1/2 whitespace-nowrap rounded-md bg-banten-navy-dark px-2.5 py-1.5 text-xs font-medium text-white shadow-lg ring-1 ring-white/15 lg:group-hover:block"
            role="tooltip"
          >
            {{ item.label }}
            <span
              class="absolute top-1/2 right-full -mt-1 border-4 border-transparent border-r-banten-navy-dark"
              aria-hidden="true"
            />
          </span>
        </RouterLink>
      </nav>
    </aside>

    <div class="flex min-h-screen flex-col">
      <header class="flex items-center justify-between gap-4 border-b border-banten-navy/10 bg-white/70 px-4 py-4 backdrop-blur sm:px-6">
        <div class="flex min-w-0 items-center gap-3">
          <button
            type="button"
            class="inline-flex rounded-md border border-banten-navy/15 p-2 text-banten-navy transition hover:bg-banten-sand lg:hidden"
            aria-label="Buka menu"
            @click="mobileOpen = true"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
          <button
            type="button"
            class="hidden rounded-md border border-banten-navy/15 p-2 text-banten-navy transition hover:bg-banten-sand lg:inline-flex"
            :title="collapsed ? 'Perluas sidebar' : 'Ciutkan sidebar'"
            @click="toggleSidebar"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5" />
            </svg>
          </button>
          <div class="min-w-0">
            <p class="text-sm text-banten-navy/60">Masuk sebagai</p>
            <p class="truncate font-medium text-banten-navy">
              {{ auth.user?.full_name }}
              <span class="text-banten-navy/50">· {{ roleName }}</span>
            </p>
          </div>
        </div>
        <div class="flex shrink-0 items-center gap-3">
          <AlertBell v-if="showAlerts" />
          <button
            type="button"
            class="rounded-md border border-banten-navy/20 px-3 py-1.5 text-sm text-banten-navy transition hover:border-banten-red hover:text-banten-red"
            @click="onLogout"
          >
            Keluar
          </button>
        </div>
      </header>
      <main class="flex-1 p-4 sm:p-6">
        <RouterView />
      </main>
      <footer class="border-t border-banten-navy/10 px-4 py-3 text-center text-xs text-banten-navy/45 sm:px-6 sm:text-left">
        {{ APP_NAME }} · {{ APP_VERSION_LABEL }}
        <span class="text-banten-navy/30"> · Biro Adpim Setda Provinsi Banten</span>
      </footer>
    </div>
  </div>
</template>
