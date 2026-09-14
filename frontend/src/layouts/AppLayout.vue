<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useLocalStorage } from '@vueuse/core'
import { APP_NAME, APP_FULL_NAME, APP_VERSION_LABEL } from '../config/app'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import AlertBell from '../components/AlertBell.vue'
import AppSwitcher from '../components/AppSwitcher.vue'
import ProjectSwitcher from '../components/ProjectSwitcher.vue'
import { useProjectStore } from '../stores/project'

const auth = useAuthStore()
const theme = useThemeStore()
const projectStore = useProjectStore()
const route = useRoute()
const collapsed = useLocalStorage('sb-sidebar-collapsed', false)
const mobileOpen = ref(false)

const navGroups = computed(() => {
  const role = auth.user?.role?.code
  const groups = [
    {
      key: 'utama',
      label: 'Utama',
      items: [
        { to: '/', label: 'Dashboard', match: 'dashboard', icon: 'chart' },
        { to: '/executive', label: 'Eksekutif', match: 'executive', icon: 'briefcase' },
      ],
    },
    {
      key: 'crisis',
      label: 'Crisis Room',
      items: [
        { to: '/crisis-room', label: 'Crisis Room', match: 'crisis-room', icon: 'radar' },
        { to: '/validasi-opd', label: 'Validasi OPD', match: 'validasi-opd', icon: 'clipboard' },
        { to: '/konten', label: 'Hub Konten', match: 'konten', icon: 'document' },
      ],
    },
    {
      key: 'media',
      label: 'Media & Amplifikasi',
      items: [
        { to: '/media-hub', label: 'Media Hub', match: 'media-hub', icon: 'newspaper' },
        { to: '/agenda', label: 'Agenda', match: 'agenda', icon: 'calendar' },
        { to: '/missions', label: 'Mission Board', match: 'missions', icon: 'flag' },
        { to: '/kol', label: 'KOL', match: 'kol', icon: 'megaphone' },
      ],
    },
    {
      key: 'laporan',
      label: 'Laporan',
      items: [
        { to: '/arsip', label: 'Arsip', match: 'arsip', icon: 'archive' },
        { to: '/reports', label: 'Laporan', match: 'reports', icon: 'document' },
      ],
    },
    {
      key: 'sistem',
      label: 'Administrasi',
      items: [
        { to: '/opds', label: 'Master OPD', match: 'opds', icon: 'clipboard' },
        { to: '/users', label: 'Users', match: 'users', icon: 'users' },
      ],
    },
  ]

  let allowed = null
  if (role === 'opd_admin') {
    allowed = ['dashboard', 'validasi-opd', 'crisis-room']
  } else if (role === 'asn') {
    allowed = ['missions']
  } else if (role === 'pimpinan') {
    allowed = [
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
    ]
  } else if (role === 'media_kol_admin') {
    allowed = ['dashboard', 'media-hub', 'agenda', 'kol', 'arsip', 'reports']
  } else if (role === 'editor') {
    allowed = [
      'dashboard',
      'crisis-room',
      'validasi-opd',
      'konten',
      'media-hub',
      'agenda',
      'missions',
      'arsip',
      'reports',
    ]
  }

  return groups
    .map((g) => ({
      ...g,
      items: allowed ? g.items.filter((i) => allowed.includes(i.match)) : g.items,
    }))
    .filter((g) => g.items.length > 0)
})

const roleName = computed(() => auth.user?.role?.name || '—')
const userInitial = computed(() => {
  const name = auth.user?.full_name || auth.user?.username || 'U'
  return name.trim().charAt(0).toUpperCase()
})
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
  // Hard navigate — avoids stuck SPA transitions from the authed layout
  window.location.assign('/login')
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
    class="h-dvh overflow-hidden bg-[#0d1117] lg:grid lg:transition-[grid-template-columns] lg:duration-300"
    :class="collapsed ? 'lg:grid-cols-[72px_1fr]' : 'lg:grid-cols-[260px_1fr]'"
  >
    <button
      v-if="mobileOpen"
      type="button"
      class="fixed inset-0 z-30 bg-black/60 lg:hidden"
      aria-label="Tutup menu"
      @click="mobileOpen = false"
    />

    <!-- Sidebar — gaya shell SIPANTAU (#161b22) -->
    <aside
      class="z-40 flex flex-col overflow-y-auto overflow-x-visible border-[#30363d] bg-[#161b22] text-[#c9d1d9] transition-all duration-300 max-lg:fixed max-lg:inset-y-0 max-lg:left-0 max-lg:w-[260px] max-lg:shadow-2xl lg:sticky lg:top-0 lg:h-dvh lg:border-r"
      :class="[
        mobileOpen ? 'max-lg:translate-x-0' : 'max-lg:-translate-x-full',
        collapsed ? 'lg:w-[72px]' : 'lg:w-auto',
      ]"
    >
      <div
        class="flex shrink-0 items-start gap-2 border-b border-[#30363d]/60 px-3 pb-4 pt-5"
        :class="collapsed ? 'lg:justify-center lg:px-2' : ''"
      >
        <RouterLink
          to="/"
          class="group min-w-0 flex-1"
          :class="collapsed ? 'lg:flex-none' : ''"
          :title="collapsed ? APP_NAME : undefined"
        >
          <div class="flex items-center gap-2.5" :class="collapsed ? 'lg:justify-center' : ''">
            <div
              class="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-emerald-500 text-sm font-black text-black shadow-sm"
            >
              <img src="/pavicon.png" :alt="APP_NAME" class="h-7 w-7 object-contain" />
            </div>
            <div class="min-w-0 flex-col" :class="collapsed ? 'lg:hidden' : 'flex'">
              <span class="text-lg font-black uppercase leading-none tracking-tight text-white">
                SIA<span class="text-emerald-400">GAPIM</span>
              </span>
              <span class="mt-1 text-[9px] font-semibold uppercase tracking-wider text-[#8b949e]">
                Respons &amp; Media Adpim
              </span>
            </div>
          </div>
          <p
            class="mt-2 text-[10px] leading-snug text-[#8b949e]"
            :class="collapsed ? 'lg:hidden' : ''"
          >
            {{ APP_FULL_NAME }}
          </p>
        </RouterLink>

        <button
          type="button"
          class="rounded-md p-2 text-[#8b949e] transition hover:bg-[#21262d] hover:text-white lg:hidden"
          aria-label="Tutup menu"
          @click="mobileOpen = false"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <nav class="flex flex-1 flex-col gap-4 px-2 py-4" :class="collapsed ? 'lg:items-center lg:gap-3 lg:px-1.5' : ''">
        <div
          v-for="(group, gi) in navGroups"
          :key="group.key"
          class="flex flex-col gap-0.5"
          :class="collapsed ? 'lg:w-full lg:items-center' : ''"
        >
          <p
            class="px-2.5 pb-1 text-[10px] font-bold uppercase tracking-wider text-[#8b949e]"
            :class="collapsed ? 'lg:sr-only' : ''"
          >
            {{ group.label }}
          </p>
          <div
            v-if="collapsed && gi > 0"
            class="mx-auto mb-1 hidden h-px w-8 bg-[#30363d] lg:block"
            aria-hidden="true"
          />
          <RouterLink
            v-for="item in group.items"
            :key="item.to"
            :to="item.to"
            class="group relative flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition"
            :class="[
              collapsed ? 'lg:w-11 lg:justify-center lg:px-0' : '',
              isActive(item)
                ? 'bg-[#2b3544] font-semibold text-white shadow-sm'
                : 'text-[#c9d1d9] hover:bg-[#21262d] hover:text-white',
            ]"
          >
            <span
              class="inline-flex h-4 w-4 shrink-0 items-center justify-center"
              :class="isActive(item) ? 'text-emerald-400' : 'text-[#8b949e] group-hover:text-[#c9d1d9]'"
            >
              <svg v-if="item.icon === 'radar'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 12m-9 0a9 9 0 1 0 18 0 9 9 0 1 0-18 0" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 12m-5 0a5 5 0 1 0 10 0 5 5 0 1 0-10 0" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 12m-1 0a1 1 0 1 0 2 0 1 1 0 1 0-2 0" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.5M19.5 8.5l-1.8 1.2" />
              </svg>
              <svg v-else-if="item.icon === 'clipboard'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5h6a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2M9 12l2 2 4-4" />
              </svg>
              <svg v-else-if="item.icon === 'document'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M14 3v5h5M9 13h6M9 17h4" />
              </svg>
              <svg v-else-if="item.icon === 'newspaper'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 5h12a2 2 0 0 1 2 2v12H6a2 2 0 0 1-2-2V5Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M18 9h2a1 1 0 0 1 1 1v7a2 2 0 0 1-2 2h-1M8 9h6M8 13h6M8 17h3" />
              </svg>
              <svg v-else-if="item.icon === 'calendar'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 4v2M17 4v2M4 9h16M6 6h12a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2Z" />
              </svg>
              <svg v-else-if="item.icon === 'flag'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 21V4m0 0h9l-1.5 3.5L14 11H5" />
              </svg>
              <svg v-else-if="item.icon === 'megaphone'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11 5.5 19 3v14l-8-2.5V5.5Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M11 14.5v3.2a1.8 1.8 0 0 1-3.5.6L7 14.5M19 8.5v5" />
              </svg>
              <svg v-else-if="item.icon === 'archive'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16v2H4V7Zm1 2v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9M10 13h4M4 5h16v2H4V5Z" />
              </svg>
              <svg v-else-if="item.icon === 'chart'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 19V5M4 19h16M8 16v-5M12 16V8M16 16v-3" />
              </svg>
              <svg v-else-if="item.icon === 'briefcase'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 6V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1M4 10h16v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8Z" />
              </svg>
              <svg v-else-if="item.icon === 'users'" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 19v-1a3 3 0 0 0-3-3H7a3 3 0 0 0-3 3v1" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" />
              </svg>
            </span>
            <span class="truncate" :class="collapsed ? 'lg:sr-only' : ''">
              {{ item.label }}
            </span>
            <span
              v-if="collapsed"
              class="pointer-events-none absolute top-1/2 left-full z-50 ml-3 hidden -translate-y-1/2 whitespace-nowrap rounded-md border border-[#30363d] bg-[#21262d] px-2.5 py-1.5 text-xs font-medium text-white shadow-lg lg:group-hover:block"
              role="tooltip"
            >
              {{ item.label }}
            </span>
          </RouterLink>
        </div>
      </nav>

      <div
        class="mt-auto border-t border-[#30363d]/60 px-3 py-3 text-[10px] text-[#8b949e]"
        :class="collapsed ? 'lg:px-1 lg:text-center' : ''"
      >
        <span :class="collapsed ? 'lg:hidden' : ''">{{ APP_VERSION_LABEL }} · Adpim Banten</span>
        <span class="hidden" :class="collapsed ? 'lg:inline' : ''">{{ APP_VERSION_LABEL }}</span>
      </div>
    </aside>

    <div class="flex h-dvh min-h-0 min-w-0 flex-col overflow-hidden bg-[#0d1117]">
      <!-- Topbar — gaya SIPANTAU -->
      <header
        class="flex h-16 shrink-0 items-center justify-between gap-3 border-b border-[#30363d] bg-[#0d1117] px-4 shadow-sm sm:px-6"
      >
        <div class="flex min-w-0 items-center gap-3">
          <button
            type="button"
            class="inline-flex rounded-lg border border-[#30363d] bg-[#161b22] p-2 text-[#c9d1d9] transition hover:bg-[#21262d] hover:text-white lg:hidden"
            aria-label="Buka menu"
            @click="mobileOpen = true"
          >
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
          <AppSwitcher />

          <div class="hidden min-w-0 sm:block">
            <p class="truncate text-xs text-[#8b949e]">
              {{ auth.user?.full_name }}
              <span class="text-[#6e7681]">· {{ roleName }}</span>
            </p>
          </div>
        </div>

        <div class="flex shrink-0 items-center gap-2.5">
          <ProjectSwitcher />
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-lg border border-[#30363d] bg-[#161b22] p-2 text-[#c9d1d9] transition hover:bg-[#21262d] hover:text-white"
            :title="theme.isDark ? 'Mode terang' : 'Mode gelap'"
            :aria-label="theme.isDark ? 'Aktifkan mode terang' : 'Aktifkan mode gelap'"
            @click="theme.toggle()"
          >
            <!-- sun -->
            <svg
              v-if="theme.isDark"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.75"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 3v2.25M12 18.75V21M4.5 12H2.25M21.75 12H19.5M6.34 6.34 4.76 4.76M19.24 19.24l-1.58-1.58M6.34 17.66l-1.58 1.58M19.24 4.76l-1.58 1.58M16.5 12a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z"
              />
            </svg>
            <!-- moon -->
            <svg
              v-else
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.75"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z"
              />
            </svg>
          </button>
          <AlertBell v-if="showAlerts" />
          <button
            type="button"
            class="rounded-lg border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-xs font-semibold text-[#c9d1d9] transition hover:border-rose-500/40 hover:text-rose-400"
            @click="onLogout"
          >
            Keluar
          </button>
          <div
            class="flex h-8 w-8 items-center justify-center rounded-full border border-[#30363d] bg-[#21262d] text-xs font-bold text-white"
            :title="auth.user?.full_name"
          >
            {{ userInitial }}
          </div>
        </div>
      </header>

      <main
        class="min-h-0 flex-1 overflow-y-auto p-4 transition-colors sm:p-6"
        :class="theme.isDark ? 'bg-[#0d1117] text-[#c9d1d9]' : 'bg-[#f0f3f7] text-banten-navy'"
      >
        <RouterView :key="projectStore.selectedId || 'no-project'" />
      </main>
      <footer class="shrink-0 border-t border-[#30363d] bg-[#0d1117] px-4 py-2.5 text-center text-[11px] text-[#8b949e] sm:px-6 sm:text-left">
        {{ APP_NAME }} · {{ APP_VERSION_LABEL }}
        <span class="text-[#6e7681]"> · Biro Adpim Setda Provinsi Banten</span>
      </footer>
    </div>
  </div>
</template>
