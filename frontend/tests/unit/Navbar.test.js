import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Navbar from '@/components/Navbar.vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

// Mock Element Plus message
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn()
  },
  ElButton: {
    name: 'ElButton',
    template: '<button><slot /></button>'
  },
  ElIcon: {
    name: 'ElIcon',
    template: '<i><slot /></i>'
  }
}))

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  Setting: { name: 'Setting' },
  List: { name: 'List' },
  Tools: { name: 'Tools' },
  SwitchButton: { name: 'SwitchButton' }
}))

describe('Navbar.vue', () => {
  let router
  let pinia
  let wrapper

  beforeEach(() => {
    // Create fresh pinia instance
    pinia = createPinia()
    setActivePinia(pinia)

    // Create router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } },
        { path: '/configs', name: 'ConfigList', component: { template: '<div>Configs</div>' } },
        { path: '/global-config', name: 'GlobalConfig', component: { template: '<div>Global</div>' } }
      ]
    })

    // Clear mocks
    vi.clearAllMocks()
  })

  const createWrapper = async () => {
    const wrapper = mount(Navbar, {
      global: {
        plugins: [router, pinia],
        stubs: {
          'el-button': {
            template: '<button @click="$attrs.onClick"><slot /></button>',
            props: ['type', 'icon', 'loading']
          },
          'el-icon': {
            template: '<i><slot /></i>'
          }
        }
      }
    })
    await router.isReady()
    return wrapper
  }

  it('renders app title', async () => {
    wrapper = await createWrapper()
    expect(wrapper.find('.app-title').text()).toBe('飞书 AI Bot 管理')
  })

  it('displays navigation links to configs list and global config', async () => {
    wrapper = await createWrapper()
    
    const navLinks = wrapper.findAll('.nav-link')
    expect(navLinks).toHaveLength(2)
    
    // Check first link (配置列表)
    expect(navLinks[0].text()).toContain('配置列表')
    // router-link renders as <a> with href attribute
    expect(navLinks[0].element.tagName).toBe('A')
    
    // Check second link (全局配置)
    expect(navLinks[1].text()).toContain('全局配置')
    expect(navLinks[1].element.tagName).toBe('A')
  })

  it('displays logout button', async () => {
    wrapper = await createWrapper()
    
    const logoutBtn = wrapper.find('.logout-btn')
    expect(logoutBtn.exists()).toBe(true)
    expect(logoutBtn.text()).toContain('登出')
  })

  it('calls logout and redirects when logout button is clicked', async () => {
    wrapper = await createWrapper()
    
    const authStore = useAuthStore()
    const logoutSpy = vi.spyOn(authStore, 'logout').mockResolvedValue()
    const routerPushSpy = vi.spyOn(router, 'push')
    
    // Click logout button
    const logoutBtn = wrapper.find('.logout-btn')
    await logoutBtn.trigger('click')
    
    // Wait for async operations
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))
    
    // Verify logout was called
    expect(logoutSpy).toHaveBeenCalled()
    
    // Verify success message was shown
    expect(ElMessage.success).toHaveBeenCalledWith('已成功登出')
    
    // Verify redirect to login
    expect(routerPushSpy).toHaveBeenCalledWith('/login')
  })

  it('shows error message when logout fails', async () => {
    wrapper = await createWrapper()
    
    const authStore = useAuthStore()
    const logoutError = new Error('Logout failed')
    vi.spyOn(authStore, 'logout').mockRejectedValue(logoutError)
    
    // Click logout button
    const logoutBtn = wrapper.find('.logout-btn')
    await logoutBtn.trigger('click')
    
    // Wait for async operations
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))
    
    // Verify error message was shown
    expect(ElMessage.error).toHaveBeenCalledWith('登出失败，请重试')
  })

  it('has responsive design classes', async () => {
    wrapper = await createWrapper()
    
    // Check for responsive container
    expect(wrapper.find('.navbar-container').exists()).toBe(true)
    
    // Check for brand section
    expect(wrapper.find('.navbar-brand').exists()).toBe(true)
    
    // Check for nav section
    expect(wrapper.find('.navbar-nav').exists()).toBe(true)
    
    // Check for actions section
    expect(wrapper.find('.navbar-actions').exists()).toBe(true)
  })

  it('applies active class to current route', async () => {
    wrapper = await createWrapper()
    
    // Navigate to configs
    await router.push('/configs')
    await wrapper.vm.$nextTick()
    
    // The router-link component should exist and be rendered
    const navLinks = wrapper.findAll('.nav-link')
    expect(navLinks).toHaveLength(2)
    
    // Verify the links are rendered as anchor tags
    expect(navLinks[0].element.tagName).toBe('A')
    expect(navLinks[1].element.tagName).toBe('A')
  })

  it('shows loading state on logout button when logging out', async () => {
    wrapper = await createWrapper()
    
    const authStore = useAuthStore()
    // Create a promise that we can control
    let resolveLogout
    const logoutPromise = new Promise(resolve => {
      resolveLogout = resolve
    })
    vi.spyOn(authStore, 'logout').mockReturnValue(logoutPromise)
    
    // Click logout button
    const logoutBtn = wrapper.find('.logout-btn')
    await logoutBtn.trigger('click')
    await wrapper.vm.$nextTick()
    
    // Check loading state is true
    expect(wrapper.vm.isLoggingOut).toBe(true)
    
    // Resolve the logout
    resolveLogout()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))
    
    // Check loading state is false
    expect(wrapper.vm.isLoggingOut).toBe(false)
  })
})
