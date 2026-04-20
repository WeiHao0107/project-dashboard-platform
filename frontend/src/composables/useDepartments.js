import { ref, watch } from 'vue'
import { api } from '../api/index.js'

export function useDepartments(projectKey) {
  const departments = ref([])
  const loading     = ref(false)

  async function fetchDepartments() {
    if (!projectKey.value) {
      departments.value = []
      return
    }
    loading.value = true
    try {
      const res         = await api.getDepartments(projectKey.value)
      departments.value = res.data
    } catch {
      departments.value = []
    } finally {
      loading.value = false
    }
  }

  watch(projectKey, fetchDepartments, { immediate: true })

  return { departments, loading }
}
