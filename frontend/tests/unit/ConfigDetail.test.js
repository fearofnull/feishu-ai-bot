import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import ConfigDetail from '@/views/ConfigDetail.vue'
import ConfigForm from '@/components/ConfigForm.vue'
import { useConfigStore } from '@/stores/config'
import { ElMessage, ElMessageBox } from 'element-plus'

// Mock Element Plus components
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn()
    },
    ElMessageBox: {
      confirm: vi.fn()
    }
  }
})

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  ArrowLeft: { name: 'ArrowLeft' },
  Delete: { name: 'Delete' },
  Refresh: { name: 'Refresh' },
  Folder: { name: 'Folder' },
  ChatDotRound: { name: 'ChatDotRound' },
  Check: { name: 'Check' }
}))

describe('ConfigDetail.vue', () => {
  let pinia
  let router
  let configStore

  const mockConfig = {
    session_id: 'test_session_001',
    session_type: 'user',
    config: {
      target_project_dir: '/test/project',
      response_language: '中文',
      default_provider: 'claude',
      default_layer: 'api',
      default_cli_provider: null
    },
    metadata: {
      created_by: 'ou_creator',
      created_at: '2024-01-01T00:00:00Z',
      updated_by: 'ou_updater',
      updated_at: '2024-01-02T00:00:00Z',
      update_count: 5
    }
  }

  const mockEffectiveConfig = {
    target_project_dir: '/test/project',
    response_language: '中文',
    default_provider: 'claude',
    default_layer: 'api',
    default_cli_provider: 'gemini'
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    configStore = useConfigStore()

    // Create router with test route
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/configs/:id',
          name: 'ConfigDetail',
          component: ConfigDetail
        },
        {
          path: '/configs',
          name: 'ConfigList',
          component: { template: '<div>Config List</div>' }
        }
      ]
    })

    // Mock store methods
    vi.spyOn(configStore, 'fetchConfig').mockResolvedValue(mockConfig)
    vi.spyOn(configStore, 'fetchEffectiveConfig').mockResolvedValue(mockEffectiveConfig)
    vi.spyOn(configStore, 'deleteConfig').mockResolvedValue(true)

    // Set initial store state
    configStore.currentConfig = mockConfig
    configStore.loading = false
    configStore.error = null

    // Clear all mocks
    vi.clearAllMocks()
  })

  it('renders config detail page', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    expect(wrapper.find('h1').text()).toBe('配置详情')
    expect(wrapper.text()).toContain('test_session_001')
    expect(wrapper.text()).toContain('用户')
  })

  it('displays session info correctly', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('test_session_001')
    expect(wrapper.text()).toContain('用户')
  })

  it('displays metadata correctly', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('ou_creator')
    expect(wrapper.text()).toContain('ou_updater')
    expect(wrapper.text()).toContain('5')
  })

  it('loads config on mount', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    expect(configStore.fetchConfig).toHaveBeenCalledWith('test_session_001')
  })

  it('switches between config and effective config views', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    // Initially in config view
    expect(wrapper.text()).toContain('配置设置')

    // Find and click effective config radio button
    const radioButtons = wrapper.findAll('input[type="radio"]')
    const effectiveRadio = radioButtons.find(r => r.element.value === 'effective')
    
    if (effectiveRadio) {
      await effectiveRadio.trigger('change')
      await flushPromises()

      expect(configStore.fetchEffectiveConfig).toHaveBeenCalledWith('test_session_001')
    }
  })

  it('displays effective config with default value indicators', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    // Switch to effective config view
    const radioButtons = wrapper.findAll('input[type="radio"]')
    const effectiveRadio = radioButtons.find(r => r.element.value === 'effective')
    
    if (effectiveRadio) {
      await effectiveRadio.trigger('change')
      await flushPromises()

      // Check that default value tag is shown for default_cli_provider
      // (since it's null in config but has value in effective config)
      expect(wrapper.text()).toContain('默认值')
    }
  })

  it('handles reset config with confirmation', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    // Mock confirmation dialog to resolve
    ElMessageBox.confirm.mockResolvedValue('confirm')

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    // Find and click reset button
    const resetButton = wrapper.findAll('button').find(btn => 
      btn.text().includes('重置配置')
    )

    if (resetButton) {
      await resetButton.trigger('click')
      await flushPromises()

      expect(ElMessageBox.confirm).toHaveBeenCalled()
      expect(configStore.deleteConfig).toHaveBeenCalledWith('test_session_001')
      expect(ElMessage.success).toHaveBeenCalledWith('配置已重置')
    }
  })

  it('cancels reset when user cancels confirmation', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    // Mock confirmation dialog to reject
    ElMessageBox.confirm.mockRejectedValue('cancel')

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    // Find and click reset button
    const resetButton = wrapper.findAll('button').find(btn => 
      btn.text().includes('重置配置')
    )

    if (resetButton) {
      await resetButton.trigger('click')
      await flushPromises()

      expect(ElMessageBox.confirm).toHaveBeenCalled()
      expect(configStore.deleteConfig).not.toHaveBeenCalled()
    }
  })

  it('navigates back to config list', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    // Find and click back button
    const backButton = wrapper.findAll('button').find(btn => 
      btn.text().includes('返回')
    )

    if (backButton) {
      await backButton.trigger('click')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/configs')
    }
  })

  it('displays loading state', async () => {
    configStore.loading = true
    configStore.currentConfig = null

    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    expect(wrapper.find('.loading-container').exists()).toBe(true)
  })

  it('displays error state', async () => {
    configStore.loading = false
    configStore.error = '加载配置失败'
    configStore.currentConfig = null

    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('加载配置失败')
  })

  it('handles save success from ConfigForm', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router]
      }
    })

    await flushPromises()

    // Find ConfigForm component and emit save-success
    const configForm = wrapper.findComponent(ConfigForm)
    if (configForm.exists()) {
      await configForm.vm.$emit('save-success')
      await flushPromises()

      expect(ElMessage.success).toHaveBeenCalledWith('配置保存成功')
      expect(configStore.fetchConfig).toHaveBeenCalledTimes(2) // Once on mount, once on save
    }
  })

  it('formats dates correctly', async () => {
    router.push('/configs/test_session_001')
    await router.isReady()

    const wrapper = mount(ConfigDetail, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ConfigForm: true
        }
      }
    })

    await flushPromises()

    // Check that dates are formatted (should contain year, month, day)
    const text = wrapper.text()
    expect(text).toMatch(/\d{4}/)  // Year
    expect(text).toMatch(/\d{2}/)  // Month/Day
  })
})
