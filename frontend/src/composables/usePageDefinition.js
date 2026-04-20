import { ref, watch } from 'vue'
import { api } from '../api/index.js'

export function usePageDefinition(projectKey, pageId) {
  const pageDef = ref(null)
  const loading = ref(false)
  const error   = ref(null)

  async function fetchPage() {
    if (!projectKey.value || !pageId.value) {
      pageDef.value = null
      return
    }
    loading.value = true
    error.value   = null
    try {
      const res     = await api.getPage(projectKey.value, pageId.value)
      pageDef.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  watch([projectKey, pageId], fetchPage, { immediate: true })

  return { pageDef, loading, error }
}
