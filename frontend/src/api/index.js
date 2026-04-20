import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const api = {
  // Projects
  getProjects() {
    return http.get('/projects')
  },

  getDepartments(projectKey) {
    return http.get(`/projects/${projectKey}/departments`)
  },

  // Pages
  getPages(projectKey) {
    return http.get(`/projects/${projectKey}/pages`)
  },

  getPage(projectKey, pageId) {
    return http.get(`/projects/${projectKey}/pages/${pageId}`)
  },

  // Widget data
  queryWidgetData({ projectKey, pageId, widgetId, dataSource, filters }) {
    return http.post('/widget-data/query', {
      projectKey,
      pageId,
      widgetId,
      dataSource,
      filters,
    })
  },
}
