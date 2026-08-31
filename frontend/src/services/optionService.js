import { apiClient } from '@/lib/api'

export const optionService = {
  async getSources() {
    const { data } = await apiClient.get('/options/sources')
    return data
  },

  async getItems(sourceKey) {
    const { data } = await apiClient.get(`/options/${sourceKey}`)
    return data
  },

  async createItem(sourceKey, label) {
    const { data } = await apiClient.post(`/options/${sourceKey}`, { label })
    return data
  },

  async updateItem(sourceKey, itemId, label) {
    const { data } = await apiClient.put(`/options/${sourceKey}/${itemId}`, { label })
    return data
  },

  async deleteItem(sourceKey, itemId) {
    const { data } = await apiClient.delete(`/options/${sourceKey}/${itemId}`)
    return data
  },
}
