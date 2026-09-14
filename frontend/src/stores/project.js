import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../services/api'

const PROJECT_KEY = 'sb_sipantau_project_id'

export const useProjectStore = defineStore('project', () => {
  const projects = ref([])
  const selectedId = ref(localStorage.getItem(PROJECT_KEY) || '')
  const loading = ref(false)
  const error = ref('')
  const source = ref('')
  const ready = ref(false)

  const selectedProject = computed(
    () => projects.value.find((p) => p.id === selectedId.value) || null,
  )

  const label = computed(() => selectedProject.value?.name || 'Pilih project')

  function setSelectedId(id) {
    if (!id) return
    selectedId.value = id
    localStorage.setItem(PROJECT_KEY, id)
  }

  function ensureSelection() {
    if (!projects.value.length) {
      selectedId.value = ''
      localStorage.removeItem(PROJECT_KEY)
      return
    }
    if (!selectedId.value || !projects.value.some((p) => p.id === selectedId.value)) {
      setSelectedId(projects.value[0].id)
    }
  }

  async function loadProjects() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/dashboard/projects')
      projects.value = data.data || []
      source.value = data.source || ''
      ensureSelection()
    } catch (err) {
      error.value = err.response?.data?.error || 'Gagal memuat project SIPANTAU'
      projects.value = []
    } finally {
      loading.value = false
      ready.value = true
    }
  }

  return {
    projects,
    selectedId,
    selectedProject,
    label,
    loading,
    error,
    source,
    ready,
    setSelectedId,
    loadProjects,
    ensureSelection,
  }
})
