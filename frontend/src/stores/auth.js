import axios from 'axios'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const TOKEN_KEY = 'sb_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(null)
  const ready = ref(false)
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => Boolean(token.value && user.value))

  function setToken(value) {
    token.value = value
    if (value) localStorage.setItem(TOKEN_KEY, value)
    else localStorage.removeItem(TOKEN_KEY)
  }

  async function login(username, password) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await axios.post('/api/auth/login', { username, password })
      setToken(data.access_token)
      user.value = data.user
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Login gagal'
      setToken('')
      user.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  async function bootstrap() {
    if (!token.value) {
      ready.value = true
      return
    }
    try {
      const { data } = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      user.value = data.user
    } catch {
      setToken('')
      user.value = null
    } finally {
      ready.value = true
    }
  }

  async function logout() {
    try {
      if (token.value) {
        await axios.post(
          '/api/auth/logout',
          {},
          { headers: { Authorization: `Bearer ${token.value}` } },
        )
      }
    } catch {
      // ignore network errors on logout
    }
    setToken('')
    user.value = null
  }

  return {
    token,
    user,
    ready,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    bootstrap,
  }
})
