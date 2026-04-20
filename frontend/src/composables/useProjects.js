import { ref, onMounted } from 'vue'
import { api } from '../api/index.js'

export function useProjects() {
  const projects = ref([])
  const loading  = ref(false)
  const error    = ref(null)

  async function fetchProjects() {
    loading.value = true
    try {
      projects.value = (await api.getProjects()).data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  onMounted(fetchProjects)
  return { projects, loading, error }
}
