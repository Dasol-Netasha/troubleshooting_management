import { apiClient } from '@/lib/api'

export const authService = {
  async login(id, pw) {
    const { data } = await apiClient.post('/auth/login', { id, pw })
    return data
  },
}