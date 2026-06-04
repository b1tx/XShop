import { defineStore } from 'pinia'

interface UserProfile {
  id: number
  username: string
  roles: string[]
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as UserProfile | null
  }),
  actions: {
    setSession(token: string, user: UserProfile) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
    },
    clearSession() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  }
})

