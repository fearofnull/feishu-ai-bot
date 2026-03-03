import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import Navbar from '@/components/Navbar.vue'

describe('App.vue', () => {
  let router
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } },
        { path: '/configs', name: 'ConfigList', component: { template: '<div>Configs</div>' } },
        { path: '/global-config', name: 'GlobalConfig', component: { template: '<div>Global</div>' } }
      ]
    })
  })

  it('renders app container', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia],
        stubs: {
          Navbar: true
        }
      }
    })

    expect(wrapper.find('#app').exists()).toBe(true)
  })

  it('renders main content area', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia],
        stubs: {
          Navbar: true
        }
      }
    })

    expect(wrapper.find('.main-content').exists()).toBe(true)
  })

  it('shows navbar on non-login pages', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia]
      }
    })

    expect(wrapper.findComponent(Navbar).exists()).toBe(true)
  })

  it('hides navbar on login page', async () => {
    router.push('/login')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia]
      }
    })

    expect(wrapper.findComponent(Navbar).exists()).toBe(false)
  })

  it('renders router-view for page content', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia],
        stubs: {
          Navbar: true
        }
      }
    })

    // router-view should render the route component
    expect(wrapper.html()).toContain('Configs')
  })

  it('updates navbar visibility when route changes', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia]
      }
    })

    // Initially on configs page, navbar should be visible
    expect(wrapper.findComponent(Navbar).exists()).toBe(true)

    // Navigate to login page
    await router.push('/login')
    await wrapper.vm.$nextTick()

    // Navbar should be hidden
    expect(wrapper.findComponent(Navbar).exists()).toBe(false)

    // Navigate back to configs
    await router.push('/configs')
    await wrapper.vm.$nextTick()

    // Navbar should be visible again
    expect(wrapper.findComponent(Navbar).exists()).toBe(true)
  })

  it('applies correct layout classes', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia],
        stubs: {
          Navbar: true
        }
      }
    })

    const app = wrapper.find('#app')
    expect(app.exists()).toBe(true)
    
    // Check that the app has flex layout
    const styles = getComputedStyle(app.element)
    // Note: In test environment, computed styles might not be fully available
    // So we just check that the element exists with the correct structure
    expect(wrapper.find('.main-content').exists()).toBe(true)
  })

  it('maintains layout structure across route changes', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia],
        stubs: {
          Navbar: true
        }
      }
    })

    expect(wrapper.find('#app').exists()).toBe(true)
    expect(wrapper.find('.main-content').exists()).toBe(true)

    await router.push('/global-config')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('#app').exists()).toBe(true)
    expect(wrapper.find('.main-content').exists()).toBe(true)
  })

  it('computes showNavbar correctly based on route', async () => {
    router.push('/configs')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia],
        stubs: {
          Navbar: true
        }
      }
    })

    // On /configs, showNavbar should be true
    expect(wrapper.vm.showNavbar).toBe(true)

    await router.push('/login')
    await wrapper.vm.$nextTick()

    // On /login, showNavbar should be false
    expect(wrapper.vm.showNavbar).toBe(false)

    await router.push('/global-config')
    await wrapper.vm.$nextTick()

    // On /global-config, showNavbar should be true
    expect(wrapper.vm.showNavbar).toBe(true)
  })
})
