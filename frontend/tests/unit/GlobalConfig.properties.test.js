import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import GlobalConfig from '@/views/GlobalConfig.vue'
import { useConfigStore } from '@/stores/config'

// Mock Element Plus
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

/**
 * Property-Based Tests for GlobalConfig Component
 * 
 * Feature: web-admin-interface, Property 19: 全局配置只读
 * **Validates: Requirements 12.4**
 * 
 * Property: For any global configuration view request, the returned configuration 
 * should be read-only, and no modification interface should be provided.
 */
describe('GlobalConfig.vue - Property-Based Tests', () => {
  let router
  let pinia
  let wrapper
  let configStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/global-config', name: 'GlobalConfig', component: { template: '<div>GlobalConfig</div>' } }
      ]
    })

    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  // Helper to create wrapper with mocked config
  const createWrapper = async (mockConfig) => {
    vi.spyOn(useConfigStore(), 'fetchGlobalConfig').mockResolvedValue(mockConfig)
    
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
            template: '<i class="el-icon"><slot /></i>',
            props: ['size', 'color']
          },
          'el-empty': {
            template: '<div class="el-empty"><slot /></div>',
            props: ['description']
          }
        }
      }
    })
    
    await router.isReady()
    configStore = useConfigStore()
    await flushPromises()
    
    return wrapper
  }

  // Generate test configurations with various values
  const generateTestConfigs = () => {
    const providers = ['claude', 'gemini', 'openai', null, '']
    const layers = ['api', 'cli', null, '']
    const languages = ['中文', 'English', '日本語', null, '']
    const paths = ['/path/to/project', '/another/path', '', null]
    
    const configs = []
    
    // Generate combinations
    for (let i = 0; i < 10; i++) {
      configs.push({
        target_project_dir: paths[i % paths.length],
        response_language: languages[i % languages.length],
        default_provider: providers[i % providers.length],
        default_layer: layers[i % layers.length],
        default_cli_provider: providers[(i + 1) % providers.length]
      })
    }
    
    return configs
  }

  describe('Property 19: Global Configuration Read-only', () => {
    it('should not provide any edit/save/modify buttons for any configuration', async () => {
      const testConfigs = generateTestConfigs()
      
      for (const config of testConfigs) {
        wrapper = await createWrapper(config)
        
        // Check that no edit-related buttons exist
        const buttons = wrapper.findAll('button')
        const editButtons = buttons.filter(btn => {
          const text = btn.text().toLowerCase()
          return text.includes('编辑') || 
                 text.includes('保存') || 
                 text.includes('修改') ||
                 text.includes('edit') ||
                 text.includes('save') ||
                 text.includes('update')
        })
        
        expect(editButtons.length).toBe(0)
        
        wrapper.unmount()
      }
    })

    it('should not provide any input fields for any configuration', async () => {
      const testConfigs = generateTestConfigs()
      
      for (const config of testConfigs) {
        wrapper = await createWrapper(config)
        
        // Check that no input fields exist
        expect(wrapper.find('input[type="text"]').exists()).toBe(false)
        expect(wrapper.find('input[type="number"]').exists()).toBe(false)
        expect(wrapper.find('textarea').exists()).toBe(false)
        expect(wrapper.find('select').exists()).toBe(false)
        
        // Check that no editable elements exist
        const editableElements = wrapper.findAll('[contenteditable="true"]')
        expect(editableElements.length).toBe(0)
        
        wrapper.unmount()
      }
    })

    it('should display all configuration values as read-only tags for any configuration', async () => {
      const testConfigs = generateTestConfigs()
      
      for (const config of testConfigs) {
        wrapper = await createWrapper(config)
        
        // All config values should be displayed in tags (read-only)
        const tags = wrapper.findAll('.el-tag')
        
        // Should have tags for all 5 config fields
        expect(tags.length).toBeGreaterThanOrEqual(5)
        
        // Tags should not be editable
        tags.forEach(tag => {
          expect(tag.attributes('contenteditable')).toBeUndefined()
          expect(tag.find('input').exists()).toBe(false)
        })
        
        wrapper.unmount()
      }
    })

    it('should not allow modification of global config through component methods', async () => {
      const testConfig = {
        target_project_dir: '/test/path',
        response_language: '中文',
        default_provider: 'claude',
        default_layer: 'api',
        default_cli_provider: 'gemini'
      }
      
      wrapper = await createWrapper(testConfig)
      
      // Check that component doesn't have update/save methods
      expect(wrapper.vm.updateConfig).toBeUndefined()
      expect(wrapper.vm.saveConfig).toBeUndefined()
      expect(wrapper.vm.modifyConfig).toBeUndefined()
      expect(wrapper.vm.editConfig).toBeUndefined()
      
      // Only loadGlobalConfig method should exist (for refreshing)
      expect(wrapper.vm.loadGlobalConfig).toBeDefined()
      expect(typeof wrapper.vm.loadGlobalConfig).toBe('function')
    })

    it('should only allow refresh action, not modification actions', async () => {
      const testConfig = {
        target_project_dir: '/test/path',
        response_language: '中文',
        default_provider: 'claude',
        default_layer: 'api',
        default_cli_provider: null
      }
      
      wrapper = await createWrapper(testConfig)
      
      // Find all buttons
      const buttons = wrapper.findAll('button')
      
      // Should only have refresh button (and possibly other read-only actions)
      const actionButtons = buttons.filter(btn => {
        const text = btn.text()
        return text.includes('刷新') || text.includes('Refresh')
      })
      
      // Should have at least one refresh button
      expect(actionButtons.length).toBeGreaterThan(0)
      
      // Should not have any modification buttons
      const modificationButtons = buttons.filter(btn => {
        const text = btn.text()
        return text.includes('保存') || 
               text.includes('编辑') || 
               text.includes('修改') ||
               text.includes('删除') ||
               text.includes('Save') ||
               text.includes('Edit') ||
               text.includes('Update') ||
               text.includes('Delete')
      })
      
      expect(modificationButtons.length).toBe(0)
    })

    it('should maintain read-only state after refresh for any configuration', async () => {
      const testConfigs = generateTestConfigs()
      
      for (const config of testConfigs) {
        wrapper = await createWrapper(config)
        
        // Trigger refresh
        vi.spyOn(configStore, 'fetchGlobalConfig').mockResolvedValue(config)
        await wrapper.vm.loadGlobalConfig()
        await flushPromises()
        
        // After refresh, should still be read-only
        expect(wrapper.find('input').exists()).toBe(false)
        expect(wrapper.find('select').exists()).toBe(false)
        expect(wrapper.find('textarea').exists()).toBe(false)
        
        const buttons = wrapper.findAll('button')
        const editButtons = buttons.filter(btn => 
          btn.text().includes('编辑') || btn.text().includes('保存')
        )
        expect(editButtons.length).toBe(0)
        
        wrapper.unmount()
      }
    })

    it('should display configuration info alert explaining read-only nature', async () => {
      const testConfig = {
        target_project_dir: '/test/path',
        response_language: '中文',
        default_provider: 'claude',
        default_layer: 'api',
        default_cli_provider: 'gemini'
      }
      
      wrapper = await createWrapper(testConfig)
      
      // Should have info alert explaining read-only nature
      const alert = wrapper.find('.info-alert')
      expect(alert.exists()).toBe(true)
      
      const alertText = alert.text()
      expect(alertText).toContain('全局配置')
      expect(alertText).toContain('只读')
    })
  })
})
