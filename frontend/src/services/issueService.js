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

  async updateIssue(issueId, values, images = [], deletedImageIds = []) {
    const formData = new FormData()
    formData.append('values_json', JSON.stringify(values || {}))
    formData.append('deleted_image_ids_json', JSON.stringify(deletedImageIds || []))

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

  async getComments(issueId) {
    const { data } = await apiClient.get(`/issues/${issueId}/comments`)
    return data
  },

  async createComment(issueId, payload) {
    const { data } = await apiClient.post(`/issues/${issueId}/comments`, payload)
    return data
  },

  async createCommentReply(issueId, commentId, payload) {
    const { data } = await apiClient.post(`/issues/${issueId}/comments/${commentId}/reply`, payload)
    return data
  },
}
