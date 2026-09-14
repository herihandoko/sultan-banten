import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useProjectStore } from '../stores/project'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

const SKIP_PROJECT_PARAM = [
  '/auth/',
  '/dashboard/projects',
  '/users',
  '/users/roles',
  '/opds',
  '/health',
]

function shouldAttachProject(url = '') {
  const path = String(url)
  return !SKIP_PROJECT_PARAM.some((p) => path.includes(p))
}

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }

  try {
    const project = useProjectStore()
    if (project.selectedId && shouldAttachProject(config.url || '')) {
      const method = (config.method || 'get').toLowerCase()
      if (method === 'get' || method === 'delete') {
        config.params = { ...(config.params || {}), project_id: project.selectedId }
      } else {
        // Attach for writes that create issue-scoped entities
        const body = config.data
        if (body && typeof body === 'object' && !(body instanceof FormData) && !body.project_id) {
          config.data = { ...body, project_id: project.selectedId }
        } else if (!body) {
          config.data = { project_id: project.selectedId }
        }
      }
    }
  } catch {
    // Pinia may not be ready during bootstrap
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      await auth.logout()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api
