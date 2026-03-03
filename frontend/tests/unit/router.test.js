import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'
import router from '@/router'

describe('Vue Router Configuration', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  it('should have all required routes defined', () => {
    const routes = router.getRoutes()
    const routePaths = routes.map(r => r.path)
    
    expect(routePaths).toContain('/login')
    expect(routePaths).toContain('/configs')
    expect(routePaths).toContain('/configs/:id')
    expect(routePaths).toContain('/global-config')
  })

  it('should redirect root path to login', () => {
    const routes = router.getRoutes()
    const rootRoute = routes.find(r => r.path === '/')
    
    expect(rootRoute).toBeDefined()
    expect(rootRoute.redirect).toBe('/login')
  })

  it('should mark protected routes with requiresAuth meta', () => {
    const routes = router.getRoutes()
    
    const configsRoute = routes.find(r => r.path === '/configs')
    expect(configsRoute.meta.requiresAuth).toBe(true)
    
    const configDetailRoute = routes.find(r => r.path === '/configs/:id')
    expect(configDetailRoute.meta.requiresAuth).toBe(true)
    
    const globalConfigRoute = routes.find(r => r.path === '/global-config')
    expect(globalConfigRoute.meta.requiresAuth).toBe(true)
  })

  it('should not require auth for login route', () => {
    const routes = router.getRoutes()
    const loginRoute = routes.find(r => r.path === '/login')
    
    expect(loginRoute.meta.requiresAuth).toBeUndefined()
  })

  it('should redirect to login when accessing protected route without token', async () => {
    // Ensure no token in localStorage
    localStorage.removeItem('token')
    
    // Try to navigate to protected route
    await router.push('/configs')
    
    // Should redirect to login
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('should allow access to protected route with valid token', async () => {
    // Set token in localStorage
    localStorage.setItem('token', 'test-token')
    
    // Navigate to protected route
    await router.push('/configs')
    
    // Should stay on configs route
    expect(router.currentRoute.value.path).toBe('/configs')
  })

  it('should redirect to configs when accessing login with valid token', async () => {
    // Set token in localStorage
    localStorage.setItem('token', 'test-token')
    
    // Try to navigate to login
    await router.push('/login')
    
    // Should redirect to configs
    expect(router.currentRoute.value.path).toBe('/configs')
  })

  it('should allow access to login without token', async () => {
    // Ensure no token in localStorage
    localStorage.removeItem('token')
    
    // Navigate to login
    await router.push('/login')
    
    // Should stay on login route
    expect(router.currentRoute.value.path).toBe('/login')
  })
})
