import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})

export const issueApi = {
  getListPageData(params) {
    return apiClient.get('/issues/list-page', { params })
  },
  getDetail(issueId) {
    return apiClient.get(`/issues/${issueId}`)
  },
}
