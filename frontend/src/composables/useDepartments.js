import { ref, watch } from 'vue'
import { api } from '../api/index.js'

export function useDepartments(projectKey) {
  const departments = ref([])

  async function fetch() {
    if (!projectKey.value) { departments.value = []; return }
    try {
      departments.value = (await api.getDepartments(projectKey.value)).data
    } catch {
      departments.value = []
    }
  }

  watch(projectKey, fetch, { immediate: true })
  return { departments }
}
