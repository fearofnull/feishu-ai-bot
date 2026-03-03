import { defineStore } from 'pinia'
import { authAPI } from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
    user: null
  }),
  
  getters: {
    // Computed property for authentication status
    isLoggedIn: (state) => state.isAuthenticated
  },
  
  actions: {
    /**
     * Login with password
     * Calls API, stores token to localStorage, and updates state
     * @param {string} password - Admin password
     * @returns {Promise<void>}
     * @throws {Error} If login fails
     */
    async login(password) {
      try {
        const response = await authAPI.login(password)
        const { token, expires_in } = response.data.data
        
        // Store token to localStorage
        localStorage.setItem('token', token)
        
        // Update state
        this.token = token
        this.isAuthenticated = true
        
        // Optionally store expiration time
        if (expires_in) {
          const expiresAt = Date.now() + expires_in * 1000
          localStorage.setItem('token_expires_at', expiresAt.toString())
        }
        
        return response.data
      } catch (error) {
        // Clear any existing token on login failure
        this.logout()
        throw error
      }
    },
    
    /**
     * Logout user
     * Clears token from localStorage and resets state
     */
    async logout() {
      try {
        // Call logout API (optional, for server-side cleanup)
        await authAPI.logout()
      } catch (error) {
        // Continue with logout even if API call fails
        console.error('Logout API call failed:', error)
      } finally {
        // Clear token from localStorage
        localStorage.removeItem('token')
        localStorage.removeItem('token_expires_at')
        
        // Reset state
        this.token = null
        this.isAuthenticated = false
        this.user = null
      }
    },
    
    /**
     * Check authentication status
     * Verifies token validity and updates state
     * @returns {boolean} True if authenticated, false otherwise
     */
    checkAuth() {
      const token = localStorage.getItem('token')
      const expiresAt = localStorage.getItem('token_expires_at')
      
      if (!token) {
        this.isAuthenticated = false
        this.token = null
        return false
      }
      
      // Check if token has expired
      if (expiresAt) {
        const now = Date.now()
        if (now >= parseInt(expiresAt)) {
          // Token expired, clear it synchronously (no API call)
          localStorage.removeItem('token')
          localStorage.removeItem('token_expires_at')
          this.token = null
          this.isAuthenticated = false
          this.user = null
          return false
        }
      }
      
      // Token exists and hasn't expired
      this.token = token
      this.isAuthenticated = true
      return true
    }
  }
})
