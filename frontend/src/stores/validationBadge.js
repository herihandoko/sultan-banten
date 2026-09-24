import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

export const useValidationBadgeStore = defineStore('validationBadge', () => {
  const waiting = ref(0)

  async function refresh() {
    try {
      const { data } = await api.get('/validations/summary')
      waiting.value = Number(data?.data?.waiting) || 0
    } catch {
      waiting.value = 0
    }
  }

  return { waiting, refresh }
})
