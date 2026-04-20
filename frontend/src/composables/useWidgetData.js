import { ref, watch } from 'vue'
import { api } from '../api/index.js'

export function useWidgetData(projectKey, widgetDef, pageId, filters) {
  const data    = ref(null)
  const loading = ref(false)
  const error   = ref(null)

  async function fetchData() {
    if (!projectKey.value || !widgetDef.value) return
    loading.value = true
    error.value   = null
    try {
      const res = await api.queryWidgetData({
        projectKey: projectKey.value,
        pageId:     pageId.value,
        widgetId:   widgetDef.value.widgetId,
        dataSource: widgetDef.value.dataSource,
        filters:    filters.value,
      })
      data.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  watch([projectKey, widgetDef, filters], fetchData, { immediate: true, deep: true })

  return { data, loading, error }
}
