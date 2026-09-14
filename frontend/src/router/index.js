import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      component: () => import('../layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
        },
        {
          path: 'crisis-room',
          name: 'crisis-room',
          component: () => import('../views/CrisisRoomView.vue'),
        },
        {
          path: 'issues/:id',
          name: 'issue-detail',
          component: () => import('../views/IssueDetailView.vue'),
        },
        {
          path: 'validasi-opd',
          name: 'validasi-opd',
          component: () => import('../views/OpdValidationView.vue'),
        },
        {
          path: 'konten',
          name: 'konten',
          component: () => import('../views/ContentHubView.vue'),
        },
        {
          path: 'konten/:id',
          name: 'konten-detail',
          component: () => import('../views/ContentDetailView.vue'),
        },
        {
          path: 'media-hub',
          name: 'media-hub',
          component: () => import('../views/MediaHubView.vue'),
        },
        {
          path: 'missions',
          name: 'missions',
          component: () => import('../views/MissionBoardView.vue'),
        },
        {
          path: 'kol',
          name: 'kol',
          component: () => import('../views/KolView.vue'),
        },
        {
          path: 'agenda',
          name: 'agenda',
          component: () => import('../views/AgendaView.vue'),
        },
        {
          path: 'arsip',
          name: 'arsip',
          component: () => import('../views/ArchiveView.vue'),
        },
        {
          path: 'executive',
          name: 'executive',
          component: () => import('../views/ExecutiveView.vue'),
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/ReportsView.vue'),
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('../views/UsersView.vue'),
          meta: { roles: ['super_admin'] },
        },
        {
          path: 'opds',
          name: 'opds',
          component: () => import('../views/OpdMasterView.vue'),
          meta: { roles: ['super_admin'] },
        },
      ],
    },
  ],
})

function defaultHome(role) {
  if (role === 'asn') return { name: 'missions' }
  if (role === 'opd_admin') return { name: 'validasi-opd' }
  if (role === 'pimpinan') return { name: 'dashboard' }
  return { name: 'dashboard' }
}

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) {
    await auth.bootstrap()
  }
  const needsAuth = to.matched.some((r) => r.meta.requiresAuth)
  const isGuest = to.matched.some((r) => r.meta.guest)
  if (needsAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (isGuest && auth.isAuthenticated) {
    return defaultHome(auth.user?.role?.code)
  }
  if (
    (to.name === 'dashboard' || to.name === 'crisis-room')
    && auth.user?.role?.code === 'asn'
  ) {
    return { name: 'missions' }
  }
  const allowed = to.meta.roles
  if (allowed?.length && !allowed.includes(auth.user?.role?.code)) {
    return defaultHome(auth.user?.role?.code)
  }
  return true
})

export default router
