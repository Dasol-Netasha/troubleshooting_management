import { apiClient } from '@/lib/api'

export const issueService = {
  async getListPageData(params) {
    const { data } = await apiClient.get('/issues/list-page', { params })
    return data
  },

  async getDetail(issueId) {
    const { data } = await apiClient.get(`/issues/${issueId}`)
    return data
  },

  async getFormConfig() {
    const { data } = await apiClient.get('/issues/form-config')
    return data
  },

  async getFormData(issueId) {
    const { data } = await apiClient.get(`/issues/${issueId}/form`)
    return data
  },

  async createIssue(values) {
    const { data } = await apiClient.post('/issues', { values })
    return data
  },

  async updateIssue(issueId, values) {
    const { data } = await apiClient.put(`/issues/${issueId}`, { values })
    return data
  },

  async deleteIssue(issueId) {
    const { data } = await apiClient.delete(`/issues/${issueId}`)
    return data
  },
}
