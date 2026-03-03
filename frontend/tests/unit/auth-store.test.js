import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../../src/stores/auth.js'
import { authAPI } from '../../src/api/client.js'

// Mock the API client
vi.mock('../../src/api/client.js', () => ({
  authAPI: {
    login: vi.fn(),
    logout: vi.fn()
  }
}))

describe('Auth Store', () => {
  let store

  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia())
    store = useAuthStore()
    
    // Clear localStorage
    localStorage.clear()
    
    // Clear all mocks
    vi.clearAllMocks()
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe('Initial State', () => {
    it('should initialize with no token and not authenticated', () => {
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
    })

    it('should initialize with token from localStorage if present', () => {
      localStorage.setItem('token', 'existing-token')
      
      // Create new store instance to test initialization
      setActivePinia(createPinia())
      const newStore = useAuthStore()
      
      expect(newStore.token).toBe('existing-token')
      expect(newStore.isAuthenticated).toBe(true)
    })
  })

  describe('Getters', () => {
    it('should have isLoggedIn getter that returns authentication status', () => {
      expect(store.isLoggedIn).toBe(false)
      
      store.isAuthenticated = true
      expect(store.isLoggedIn).toBe(true)
    })
  })

  describe('login action', () => {
    it('should successfully login with correct password', async () => {
      const mockToken = 'test-token-123'
      const mockResponse = {
        data: {
          data: {
            token: mockToken,
            expires_in: 7200
          }
        }
      }
      
      authAPI.login.mockResolvedValue(mockResponse)
      
      await store.login('correct-password')
      
      expect(authAPI.login).toHaveBeenCalledWith('correct-password')
      expect(store.token).toBe(mockToken)
      expect(store.isAuthenticated).toBe(true)
      expect(localStorage.getItem('token')).toBe(mockToken)
      expect(localStorage.getItem('token_expires_at')).toBeTruthy()
    })

    it('should store token to localStorage', async () => {
      const mockToken = 'test-token-456'
      const mockResponse = {
        data: {
          data: {
            token: mockToken,
            expires_in: 7200
          }
        }
      }
      
      authAPI.login.mockResolvedValue(mockResponse)
      
      await store.login('password')
      
      expect(localStorage.getItem('token')).toBe(mockToken)
    })

    it('should store expiration time when provided', async () => {
      const mockToken = 'test-token-789'
      const expiresIn = 7200
      const mockResponse = {
        data: {
          data: {
            token: mockToken,
            expires_in: expiresIn
          }
        }
      }
      
      authAPI.login.mockResolvedValue(mockResponse)
      
      const beforeLogin = Date.now()
      await store.login('password')
      const afterLogin = Date.now()
      
      const storedExpiration = parseInt(localStorage.getItem('token_expires_at'))
      expect(storedExpiration).toBeGreaterThanOrEqual(beforeLogin + expiresIn * 1000)
      expect(storedExpiration).toBeLessThanOrEqual(afterLogin + expiresIn * 1000)
    })

    it('should clear token on login failure', async () => {
      // Set existing token
      localStorage.setItem('token', 'old-token')
      store.token = 'old-token'
      store.isAuthenticated = true
      
      authAPI.login.mockRejectedValue(new Error('Invalid password'))
      
      try {
        await store.login('wrong-password')
      } catch (error) {
        // Expected to throw
      }
      
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.getItem('token')).toBeNull()
    })

    it('should throw error on login failure', async () => {
      const mockError = new Error('Invalid password')
      authAPI.login.mockRejectedValue(mockError)
      
      await expect(store.login('wrong-password')).rejects.toThrow('Invalid password')
    })
  })

  describe('logout action', () => {
    it('should clear token from localStorage', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('token_expires_at', '123456789')
      store.token = 'test-token'
      store.isAuthenticated = true
      
      authAPI.logout.mockResolvedValue({})
      
      await store.logout()
      
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('token_expires_at')).toBeNull()
    })

    it('should reset authentication state', async () => {
      store.token = 'test-token'
      store.isAuthenticated = true
      store.user = { id: '123' }
      
      authAPI.logout.mockResolvedValue({})
      
      await store.logout()
      
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
    })

    it('should call logout API', async () => {
      authAPI.logout.mockResolvedValue({})
      
      await store.logout()
      
      expect(authAPI.logout).toHaveBeenCalled()
    })

    it('should clear state even if API call fails', async () => {
      store.token = 'test-token'
      store.isAuthenticated = true
      localStorage.setItem('token', 'test-token')
      
      authAPI.logout.mockRejectedValue(new Error('Network error'))
      
      await store.logout()
      
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.getItem('token')).toBeNull()
    })
  })

  describe('checkAuth action', () => {
    it('should return false when no token exists', () => {
      const result = store.checkAuth()
      
      expect(result).toBe(false)
      expect(store.isAuthenticated).toBe(false)
    })

    it('should return true when valid token exists', () => {
      const futureTime = Date.now() + 3600000 // 1 hour from now
      localStorage.setItem('token', 'valid-token')
      localStorage.setItem('token_expires_at', futureTime.toString())
      
      const result = store.checkAuth()
      
      expect(result).toBe(true)
      expect(store.isAuthenticated).toBe(true)
      expect(store.token).toBe('valid-token')
    })

    it('should return false and clear token when token is expired', () => {
      const pastTime = Date.now() - 3600000 // 1 hour ago
      localStorage.setItem('token', 'expired-token')
      localStorage.setItem('token_expires_at', pastTime.toString())
      
      const result = store.checkAuth()
      
      expect(result).toBe(false)
      expect(store.isAuthenticated).toBe(false)
      expect(store.token).toBeNull()
      expect(localStorage.getItem('token')).toBeNull()
    })

    it('should return true when token exists without expiration time', () => {
      localStorage.setItem('token', 'token-without-expiry')
      
      const result = store.checkAuth()
      
      expect(result).toBe(true)
      expect(store.isAuthenticated).toBe(true)
      expect(store.token).toBe('token-without-expiry')
    })

    it('should update state based on token validity', () => {
      // Initially no token
      expect(store.isAuthenticated).toBe(false)
      
      // Add valid token
      localStorage.setItem('token', 'new-token')
      store.checkAuth()
      
      expect(store.isAuthenticated).toBe(true)
      expect(store.token).toBe('new-token')
    })
  })

  describe('Token expiration handling', () => {
    it('should handle token expiration correctly', () => {
      const expiresAt = Date.now() + 1000 // Expires in 1 second
      localStorage.setItem('token', 'soon-to-expire')
      localStorage.setItem('token_expires_at', expiresAt.toString())
      
      // Should be valid now
      expect(store.checkAuth()).toBe(true)
      
      // Simulate time passing
      vi.useFakeTimers()
      vi.advanceTimersByTime(2000) // Advance 2 seconds
      
      // Should be expired now
      expect(store.checkAuth()).toBe(false)
      
      vi.useRealTimers()
    })
  })

  describe('Reactive state updates', () => {
    it('should reactively update isAuthenticated when token changes', async () => {
      expect(store.isAuthenticated).toBe(false)
      
      const mockResponse = {
        data: {
          data: {
            token: 'new-token',
            expires_in: 7200
          }
        }
      }
      
      authAPI.login.mockResolvedValue(mockResponse)
      
      await store.login('password')
      
      expect(store.isAuthenticated).toBe(true)
      
      await store.logout()
      
      expect(store.isAuthenticated).toBe(false)
    })
  })
})
