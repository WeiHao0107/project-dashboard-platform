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
  getIssueTrend(projectKey, { year, departmentId } = {}) {
    return http.get(`/projects/${projectKey}/issue-trend`, {
      params: { year, departmentId },
    })
  },
  getMemberPerformance(projectKey, { year, departmentId } = {}) {
    return http.get(`/projects/${projectKey}/member-performance`, {
      params: { year, departmentId },
    })
  },
}
