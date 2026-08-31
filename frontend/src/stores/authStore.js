import { ref } from 'vue'
import { defineStore } from 'pinia'
import { authService } from '@/services/authService'

const AUTH_KEY = 'auth:isAuthenticated'
const AUTH_USER_KEY = 'auth:accountId'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(sessionStorage.getItem(AUTH_KEY) === 'true')
  const accountId = ref(sessionStorage.getItem(AUTH_USER_KEY) || '')

  const login = async (id, password) => {
    try {
      const data = await authService.login(id, password)
      const success = Boolean(data?.authenticated)

      if (!success) {
        isAuthenticated.value = false
        accountId.value = ''
        sessionStorage.removeItem(AUTH_KEY)
        sessionStorage.removeItem(AUTH_USER_KEY)
        return false
      }

      isAuthenticated.value = true
      accountId.value = String(data?.account_id || id || '')
      sessionStorage.setItem(AUTH_KEY, 'true')
      sessionStorage.setItem(AUTH_USER_KEY, accountId.value)
      return true
    } catch {
      isAuthenticated.value = false
      accountId.value = ''
      sessionStorage.removeItem(AUTH_KEY)
      sessionStorage.removeItem(AUTH_USER_KEY)
      return false
    }
  }

  const logout = () => {
    isAuthenticated.value = false
    accountId.value = ''
    sessionStorage.removeItem(AUTH_KEY)
    sessionStorage.removeItem(AUTH_USER_KEY)
  }

  return {
    isAuthenticated,
    accountId,
    login,
    logout,
  }
})
