import { ref, watch } from 'vue'
import { api } from '../api/index.js'

/**
 * Fetch widget data directly — used inside dedicated page components.
 * @param {Ref<string>} projectKey
 * @param {string}      dataSource   static string (e.g. 'issue_created_resolved_trend')
 * @param {Ref<object>} filters      { year, departmentId }
 */
export function usePageData(projectKey, dataSource, filters) {
  const data    = ref(null)
  const loading = ref(false)
  const error   = ref(null)

  async function fetchData() {
    if (!projectKey.value) return
    loading.value = true
    error.value   = null
    try {
      const res = await api.queryData({
        projectKey: projectKey.value,
        dataSource,
        filters: filters.value,
      })
      data.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  watch([projectKey, filters], fetchData, { immediate: true, deep: true })

  return { data, loading, error }
}
