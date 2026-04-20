import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const api = {
  getProjects() {
    return http.get('/projects')
  },
  getDepartments(projectKey) {
    return http.get(`/projects/${projectKey}/departments`)
  },
  getPages(projectKey) {
    return http.get(`/projects/${projectKey}/pages`)
  },
  queryData({ projectKey, dataSource, filters }) {
    return http.post('/widget-data/query', { projectKey, dataSource, filters })
  },
}
