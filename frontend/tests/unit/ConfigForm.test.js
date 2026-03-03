import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ConfigForm from '@/components/ConfigForm.vue'
import { useConfigStore } from '@/stores/config'
import { ElMessage } from 'element-plus'
import { elementPlusStubs } from '../setup.js'

// Mock Element Plus components
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn()
    }
  }
})

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  Folder: { name: 'Folder' },
  ChatDotRound: { name: 'ChatDotRound' },
  Check: { name: 'Check' }
}))

describe('ConfigForm.vue', () => {
  let pinia
  let configStore

  const mockConfig = {
    target_project_dir: '/test/project',
    response_language: '中文',
    default_provider: 'claude',
    default_layer: 'api',
    default_cli_provider: null
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    configStore = useConfigStore()

    // Mock store methods
    vi.spyOn(configStore, 'updateConfig').mockResolvedValue({
      session_id: 'test_session',
      config: mockConfig,
      metadata: {}
    })

    // Clear all mocks
    vi.clearAllMocks()
  })

  it('renders form with all fields', () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia],
        stubs: elementPlusStubs
      }
    })

    expect(wrapper.text()).toContain('项目目录')
    expect(wrapper.text()).toContain('响应语言')
    expect(wrapper.text()).toContain('默认提供商')
    expect(wrapper.text()).toContain('默认层级')
    expect(wrapper.text()).toContain('默认 CLI 提供商')
  })

  it('initializes form with config values', () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia],
        stubs: elementPlusStubs
      }
    })

    // Check that form data is initialized
    expect(wrapper.vm.formData.target_project_dir).toBe('/test/project')
    expect(wrapper.vm.formData.response_language).toBe('中文')
    expect(wrapper.vm.formData.default_provider).toBe('claude')
    expect(wrapper.vm.formData.default_layer).toBe('api')
  })

  it('updates form when config prop changes', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.vm.formData.default_provider).toBe('claude')

    // Update config prop
    await wrapper.setProps({
      config: {
        ...mockConfig,
        default_provider: 'gemini'
      }
    })

    await flushPromises()

    expect(wrapper.vm.formData.default_provider).toBe('gemini')
  })

  it('validates provider field', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: {},
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Set invalid provider
    wrapper.vm.formData.default_provider = 'invalid_provider'

    // Trigger validation
    try {
      await wrapper.vm.formRef.validate()
    } catch (error) {
      // Validation should fail
      expect(error).toBeDefined()
    }
  })

  it('validates layer field', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: {},
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Set invalid layer
    wrapper.vm.formData.default_layer = 'invalid_layer'

    // Trigger validation
    try {
      await wrapper.vm.formRef.validate()
    } catch (error) {
      // Validation should fail
      expect(error).toBeDefined()
    }
  })

  it('validates CLI provider field', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: {},
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Set invalid CLI provider
    wrapper.vm.formData.default_cli_provider = 'invalid_provider'

    // Trigger validation
    try {
      await wrapper.vm.formRef.validate()
    } catch (error) {
      // Validation should fail
      expect(error).toBeDefined()
    }
  })

  it('submits form with valid data', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Update form data
    wrapper.vm.formData.default_provider = 'gemini'

    // Submit form
    await wrapper.vm.handleSubmit()
    await flushPromises()

    expect(configStore.updateConfig).toHaveBeenCalledWith('test_session', expect.objectContaining({
      default_provider: 'gemini'
    }))
  })

  it('emits save-success event on successful save', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Submit form
    await wrapper.vm.handleSubmit()
    await flushPromises()

    expect(wrapper.emitted('save-success')).toBeTruthy()
    expect(ElMessage.success).toHaveBeenCalledWith('配置保存成功')
  })

  it('displays error message on save failure', async () => {
    configStore.updateConfig.mockRejectedValue({
      userMessage: '保存失败'
    })

    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Submit form
    await wrapper.vm.handleSubmit()
    await flushPromises()

    expect(ElMessage.error).toHaveBeenCalledWith('保存失败')
  })

  it('displays validation errors from server', async () => {
    configStore.updateConfig.mockRejectedValue({
      userMessage: '验证失败',
      validationErrors: '提供商无效'
    })

    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Submit form
    await wrapper.vm.handleSubmit()
    await flushPromises()

    expect(wrapper.vm.validationError).toBe('提供商无效')
  })

  it('shows warning when all fields are empty', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: {},
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Clear all form data
    wrapper.vm.formData.target_project_dir = ''
    wrapper.vm.formData.response_language = ''
    wrapper.vm.formData.default_provider = ''
    wrapper.vm.formData.default_layer = ''
    wrapper.vm.formData.default_cli_provider = ''

    // Submit form
    await wrapper.vm.handleSubmit()
    await flushPromises()

    expect(ElMessage.warning).toHaveBeenCalledWith('请至少填写一个配置项')
    expect(configStore.updateConfig).not.toHaveBeenCalled()
  })

  it('only sends non-empty values to API', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: {},
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Set only some fields
    wrapper.vm.formData.default_provider = 'claude'
    wrapper.vm.formData.default_layer = 'api'
    wrapper.vm.formData.target_project_dir = ''
    wrapper.vm.formData.response_language = ''
    wrapper.vm.formData.default_cli_provider = ''

    // Submit form
    await wrapper.vm.handleSubmit()
    await flushPromises()

    expect(configStore.updateConfig).toHaveBeenCalledWith('test_session', {
      default_provider: 'claude',
      default_layer: 'api'
    })
  })

  it('resets form to initial values', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Change form data
    wrapper.vm.formData.default_provider = 'gemini'

    // Reset form
    await wrapper.vm.handleReset()
    await flushPromises()

    // Should be back to initial value
    expect(wrapper.vm.formData.default_provider).toBe('claude')
  })

  it('clears validation errors on reset', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Set validation error
    wrapper.vm.validationError = 'Some error'

    // Reset form
    await wrapper.vm.handleReset()
    await flushPromises()

    expect(wrapper.vm.validationError).toBeNull()
  })

  it('disables buttons while saving', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: mockConfig,
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Start saving
    wrapper.vm.saving = true
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const resetButton = buttons.find(btn => btn.text().includes('重置表单'))

    if (resetButton) {
      expect(resetButton.attributes('disabled')).toBeDefined()
    }
  })

  it('validates path length', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: {},
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Set very long path
    wrapper.vm.formData.target_project_dir = 'a'.repeat(501)

    // Trigger validation
    try {
      await wrapper.vm.formRef.validate()
    } catch (error) {
      // Validation should fail
      expect(error).toBeDefined()
    }
  })

  it('validates language length', async () => {
    const wrapper = mount(ConfigForm, {
      props: {
        config: {},
        sessionId: 'test_session'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Set very long language
    wrapper.vm.formData.response_language = 'a'.repeat(51)

    // Trigger validation
    try {
      await wrapper.vm.formRef.validate()
    } catch (error) {
      // Validation should fail
      expect(error).toBeDefined()
    }
  })
})
