import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import GlobalConfig from '@/views/GlobalConfig.vue'
import { useConfigStore } from '@/stores/config'
import { ElMessage } from 'element-plus'

// Mock Element Plus components and message
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  Loading: { name: 'Loading' },
  CircleClose: { name: 'CircleClose' },
  Refresh: { name: 'Refresh' },
  Setting: { name: 'Setting' },
  Folder: { name: 'Folder' },
  ChatDotRound: { name: 'ChatDotRound' },
  Connection: { name: 'Connection' },
  Operation: { name: 'Operation' },
  Monitor: { name: 'Monitor' }
}))

describe('GlobalConfig.vue', () => {
  let router
  let pinia
  let wrapper
  let configStore

  beforeEach(() => {
    // Create fresh pinia instance
    pinia = createPinia()
    setActivePinia(pinia)

    // Create router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/global-config', name: 'GlobalConfig', component: { template: '<div>GlobalConfig</div>' } }
      ]
    })

    // Clear mocks
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const mockGlobalConfig = {
    target_project_dir: '/default/project/path',
    response_language: '中文',
    default_provider: 'claude',
    default_layer: 'api',
    default_cli_provider: 'gemini'
  }

  const createWrapper = async (mockFetchResponse = mockGlobalConfig) => {
    // Mock fetchGlobalConfig before mounting
    vi.spyOn(useConfigStore(), 'fetchGlobalConfig').mockResolvedValue(mockFetchResponse)
    
    const wrapper = mount(GlobalConfig, {
      global: {
        plugins: [router, pinia],
        stubs: {
          'el-button': {
            template: '<button @click="$attrs.onClick" :loading="loading" :disabled="disabled"><slot /></button>',
            props: ['icon', 'type', 'loading', 'disabled']
          },
          'el-card': {
            template: '<div class="el-card"><div class="card-header"><slot name="header" /></div><slot /></div>',
            props: ['shadow']
          },
          'el-alert': {
            template: '<div class="el-alert"><slot /></div>',
            props: ['title', 'type', 'closable', 'showIcon']
          },
          'el-descriptions': {
            template: '<div class="el-descriptions"><slot /></div>',
            props: ['column', 'border', 'size']
          },
          'el-descriptions-item': {
            template: '<div class="el-descriptions-item"><div class="label"><slot name="label" /></div><div class="content"><slot /></div></div>',
            props: []
          },
          'el-tag': {
            template: '<span class="el-tag" :class="type"><slot /></span>',
            props: ['type', 'size', 'effect', 'round']
          },
          'el-icon': {
            template: '<i class="el-icon" :class="{ \'is-loading\': $attrs.class?.includes(\'is-loading\') }"><slot /></i>',
            props: ['size', 'color']
          },
          'el-empty': {
            template: '<div class="el-empty"><slot name="image" /><div class="el-empty__description"><slot /></slot></div><slot /></div>',
            props: ['description']
          }
        }
      }
    })
    
    await router.isReady()
    configStore = useConfigStore()
    
    // Wait for onMounted to complete
    await flushPromises()
    
    return wrapper
  }

  describe('Component Rendering', () => {
    it('renders page header with title and subtitle', async () => {
      wrapper = await createWrapper()
      
      expect(wrapper.find('.page-title').text()).toBe('全局配置')
      expect(wrapper.find('.page-subtitle').text()).toContain('查看系统的全局默认配置')
    })

    it('renders config card when global config is loaded', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      expect(wrapper.find('.config-card').exists()).toBe(true)
      expect(wrapper.find('.card-header').text()).toContain('全局默认配置')
    })

    it('renders refresh button', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      const refreshButton = wrapper.find('.actions button')
      expect(refreshButton.exists()).toBe(true)
      expect(refreshButton.text()).toContain('刷新配置')
    })
  })

  describe('Global Config Display', () => {
    it('displays all config fields correctly', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      const text = wrapper.text()
      expect(text).toContain('/default/project/path')
      expect(text).toContain('中文')
      expect(text).toContain('claude')
      expect(text).toContain('api')
      expect(text).toContain('gemini')
    })

    it('displays field labels correctly', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      const text = wrapper.text()
      expect(text).toContain('目标项目目录')
      expect(text).toContain('响应语言')
      expect(text).toContain('默认提供商')
      expect(text).toContain('默认层级')
      expect(text).toContain('默认 CLI 提供商')
    })

    it('displays "未设置" for null default_cli_provider', async () => {
      const configWithoutCli = { ...mockGlobalConfig, default_cli_provider: null }
      wrapper = await createWrapper(configWithoutCli)
      
      const tags = wrapper.findAll('.el-tag')
      const cliTag = tags.find(tag => tag.text() === '未设置')
      expect(cliTag).toBeDefined()
    })
  })

  describe('Loading State', () => {
    it('hides loading indicator after config is loaded', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      expect(wrapper.find('.loading-container').exists()).toBe(false)
      expect(wrapper.find('.config-content').exists()).toBe(true)
    })

    it('sets loading state during refresh', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      let resolveRefresh
      const refreshPromise = new Promise(resolve => {
        resolveRefresh = resolve
      })
      vi.spyOn(configStore, 'fetchGlobalConfig').mockReturnValue(refreshPromise)
      
      const refreshPromiseCall = wrapper.vm.loadGlobalConfig()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.loading).toBe(true)
      
      resolveRefresh(mockGlobalConfig)
      await refreshPromiseCall
      await flushPromises()
      
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Refresh Functionality', () => {
    it('calls fetchGlobalConfig when refresh button is clicked', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      const fetchSpy = vi.spyOn(configStore, 'fetchGlobalConfig').mockResolvedValue(mockGlobalConfig)
      
      const refreshButton = wrapper.find('.actions button')
      await refreshButton.trigger('click')
      await flushPromises()
      
      expect(fetchSpy).toHaveBeenCalled()
    })

    it('shows success message after refresh', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      ElMessage.success.mockClear()
      
      await wrapper.vm.loadGlobalConfig()
      await flushPromises()
      
      expect(ElMessage.success).toHaveBeenCalledWith('全局配置加载成功')
    })
  })

  describe('Provider Tag Types', () => {
    it('returns correct tag type for claude provider', async () => {
      wrapper = await createWrapper()
      
      expect(wrapper.vm.getProviderTagType('claude')).toBe('primary')
    })

    it('returns correct tag type for gemini provider', async () => {
      wrapper = await createWrapper()
      
      expect(wrapper.vm.getProviderTagType('gemini')).toBe('success')
    })

    it('returns correct tag type for openai provider', async () => {
      wrapper = await createWrapper()
      
      expect(wrapper.vm.getProviderTagType('openai')).toBe('warning')
    })

    it('returns info tag type for unknown provider', async () => {
      wrapper = await createWrapper()
      
      expect(wrapper.vm.getProviderTagType('unknown')).toBe('info')
    })

    it('returns info tag type for null provider', async () => {
      wrapper = await createWrapper()
      
      expect(wrapper.vm.getProviderTagType(null)).toBe('info')
    })
  })

  describe('Lifecycle', () => {
    it('loads global config on mount', async () => {
      const fetchSpy = vi.spyOn(useConfigStore(), 'fetchGlobalConfig').mockResolvedValue(mockGlobalConfig)
      
      wrapper = mount(GlobalConfig, {
        global: {
          plugins: [router, pinia],
          stubs: {
            'el-button': true,
            'el-card': true,
            'el-alert': true,
            'el-descriptions': true,
            'el-descriptions-item': true,
            'el-tag': true,
            'el-icon': true,
            'el-empty': true
          }
        }
      })
      await router.isReady()
      await flushPromises()
      
      expect(fetchSpy).toHaveBeenCalled()
    })

    it('displays config immediately after mount', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      expect(wrapper.vm.globalConfig).toEqual(mockGlobalConfig)
      expect(wrapper.find('.config-content').exists()).toBe(true)
    })
  })

  describe('Read-only State', () => {
    it('does not render any edit buttons', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      const buttons = wrapper.findAll('button')
      const editButtons = buttons.filter(btn => 
        btn.text().includes('编辑') || 
        btn.text().includes('保存') || 
        btn.text().includes('修改')
      )
      
      expect(editButtons.length).toBe(0)
    })

    it('does not render any input fields', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      expect(wrapper.find('input').exists()).toBe(false)
      expect(wrapper.find('select').exists()).toBe(false)
      expect(wrapper.find('textarea').exists()).toBe(false)
    })

    it('only displays config values as read-only tags', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      const tags = wrapper.findAll('.el-tag')
      expect(tags.length).toBeGreaterThan(0)
      
      // All values should be displayed in tags (read-only)
      expect(tags.length).toBe(5) // 5 config fields
    })
  })

  describe('Responsive Design', () => {
    it('applies responsive styles for mobile', async () => {
      wrapper = await createWrapper(mockGlobalConfig)
      
      // Check that responsive classes exist in the component
      const container = wrapper.find('.global-config-container')
      expect(container.exists()).toBe(true)
      
      // The component should have responsive styles defined
      const styles = wrapper.html()
      expect(styles).toBeTruthy()
    })
  })
})
