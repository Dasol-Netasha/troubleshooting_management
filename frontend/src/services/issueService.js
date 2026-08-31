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

  async createIssue(values, images = []) {
    const formData = new FormData()
    formData.append('values_json', JSON.stringify(values || {}))

    for (const image of images || []) {
      formData.append('images', image)
    }

    const { data } = await apiClient.post('/issues', formData)
    return data
  },

  async updateIssue(issueId, values, images = []) {
    const formData = new FormData()
    formData.append('values_json', JSON.stringify(values || {}))

    for (const image of images || []) {
      formData.append('images', image)
    }

    const { data } = await apiClient.put(`/issues/${issueId}`, formData)
    return data
  },

  async deleteIssue(issueId) {
    const { data } = await apiClient.delete(`/issues/${issueId}`)
    return data
  },

  async approveIssue(issueId, payload = {}) {
    const { data } = await apiClient.post(`/issues/${issueId}/approve`, payload)
    return data
  },
}
