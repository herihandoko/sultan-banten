import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../services/api'

/** @typedef {'sipantau' | 'mata_bathin'} NewsSource */

export const useNewsSourceStore = defineStore('newsSource', () => {
  /** @type {import('vue').Ref<NewsSource>} */
  const newsSource = ref('mata_bathin')
  const loaded = ref(false)
  const saving = ref(false)
  const error = ref('')

  const isSipantau = computed(() => newsSource.value === 'sipantau')
  const isMataBathin = computed(() => newsSource.value === 'mata_bathin')
  const showSipantauUi = computed(() => isSipantau.value)
  const label = computed(() => (isSipantau.value ? 'SIPANTAU' : 'Mata Bathin'))

  async function load() {
    error.value = ''
    try {
      const res = await api.get('/settings/news-source')
      const data = res.data?.data || {}
      if (data.news_source === 'sipantau' || data.news_source === 'mata_bathin') {
        newsSource.value = data.news_source
      }
    } catch (err) {
      error.value = err.response?.data?.error || 'Gagal memuat konfigurasi sumber'
    } finally {
      loaded.value = true
    }
  }

  /**
   * @param {NewsSource} source
   */
  async function setSource(source) {
    saving.value = true
    error.value = ''
    try {
      const res = await api.put('/settings/news-source', { news_source: source })
      const data = res.data?.data || {}
      newsSource.value = data.news_source || source
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Gagal menyimpan sumber berita'
      return false
    } finally {
      saving.value = false
    }
  }

  return {
    newsSource,
    loaded,
    saving,
    error,
    isSipantau,
    isMataBathin,
    showSipantauUi,
    label,
    load,
    setSource,
  }
})
