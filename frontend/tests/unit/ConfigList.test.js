import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import ConfigList from '@/views/ConfigList.vue'
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
  Refresh: { name: 'Refresh' },
  Download: { name: 'Download' },
  Upload: { name: 'Upload' },
  Search: { name: 'Search' },
  User: { name: 'User' },
  Clock: { name: 'Clock' },
  View: { name: 'View' },
  Document: { name: 'Document' }
}))

describe('ConfigList.vue', () => {
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
        { path: '/configs', name: 'ConfigList', component: { template: '<div>ConfigList</div>' } },
        { path: '/configs/:id', name: 'ConfigDetail', component: { template: '<div>ConfigDetail</div>' } }
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

  const mockConfigs = [
    {
      session_id: 'user_001',
      session_type: 'user',
      config: {
        default_provider: 'claude',
        default_layer: 'api',
        response_language: '中文'
      },
      metadata: {
        created_at: '2024-01-01T10:00:00Z',
        updated_at: '2024-01-03T10:00:00Z',
        update_count: 3
      }
    },
    {
      session_id: 'group_001',
      session_type: 'group',
      config: {
        default_provider: 'gemini',
        default_layer: 'cli',
        response_language: 'English'
      },
      metadata: {
        created_at: '2024-01-02T10:00:00Z',
        updated_at: '2024-01-02T10:00:00Z',
        update_count: 1
      }
    },
    {
      session_id: 'user_002',
      session_type: 'user',
      config: {
        default_provider: 'openai',
        default_layer: 'api'
      },
      metadata: {
        created_at: '2024-01-01T08:00:00Z',
        updated_at: '2024-01-01T08:00:00Z',
        update_count: 1
      }
    }
  ]

  const createWrapper = async (configs = []) => {
    const wrapper = mount(ConfigList, {
      global: {
        plugins: [router, pinia],
        stubs: {
          'el-button': {
            template: '<button @click="$attrs.onClick" :loading="loading" :disabled="disabled"><slot /></button>',
            props: ['icon', 'type', 'loading', 'disabled']
          },
          'el-card': {
            template: '<div class="el-card"><slot /></div>',
            props: ['shadow']
          },
          'el-input': {
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" :placeholder="placeholder" class="el-input" />',
            props: ['modelValue', 'placeholder', 'prefixIcon', 'clearable'],
            emits: ['update:modelValue', 'input']
          },
          'el-select': {
            template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value); $emit(\'change\', $event.target.value)" class="el-select"><slot /></select>',
            props: ['modelValue', 'placeholder', 'clearable'],
            emits: ['update:modelValue', 'change']
          },
          'el-option': {
            template: '<option :value="value"><slot /></option>',
            props: ['label', 'value']
          },
          'el-radio-group': {
            template: '<div class="el-radio-group"><slot /></div>',
            props: ['modelValue'],
            emits: ['update:modelValue', 'change']
          },
          'el-radio-button': {
            template: '<button @click="$emit(\'click\')" :class="{ active: modelValue === label }" class="el-radio-button"><slot /></button>',
            props: ['label', 'modelValue'],
            emits: ['click']
          },
          'el-table': {
            template: '<table class="el-table"><slot /></table>',
            props: ['data', 'stripe', 'loading', 'emptyText', 'rowClassName'],
            emits: ['row-click']
          },
          'el-table-column': {
            template: '<td><slot :row="row" /></td>',
            props: ['prop', 'label', 'width', 'minWidth', 'align', 'fixed', 'showOverflowTooltip']
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
            template: '<div class="el-empty"><slot name="image" /><div class="el-empty__description"><slot /></slot></div><slot /></div>',
            props: ['description']
          }
        }
      }
    })
    
    await router.isReady()
    configStore = useConfigStore()
    
    // Set mock configs
    configStore.configs = configs
    
    return wrapper
  }

  describe('Component Rendering', () => {
    it('renders page header with title and subtitle', async () => {
      wrapper = await createWrapper()
      
      expect(wrapper.find('.page-title').text()).toBe('会话配置管理')
      expect(wrapper.find('.page-subtitle').text()).toBe('查看和管理所有会话的配置信息')
    })

    it('renders toolbar buttons', async () => {
      wrapper = await createWrapper()
      
      const buttons = wrapper.findAll('button')
      const buttonTexts = buttons.map(b => b.text())
      
      expect(buttonTexts).toContain('刷新')
      expect(buttonTexts).toContain('导出配置')
      expect(buttonTexts).toContain('导入配置')
    })

    it('renders search input', async () => {
      wrapper = await createWrapper()
      
      const searchInput = wrapper.find('.search-input input')
      expect(searchInput.exists()).toBe(true)
      expect(searchInput.attributes('placeholder')).toBe('搜索 Session ID...')
    })

    it('renders filter select', async () => {
      wrapper = await createWrapper()
      
      const filterSelect = wrapper.find('.filter-select select')
      expect(filterSelect.exists()).toBe(true)
    })

    it('renders sort radio buttons', async () => {
      wrapper = await createWrapper()
      
      const radioButtons = wrapper.findAll('.el-radio-button')
      expect(radioButtons).toHaveLength(2)
      expect(radioButtons[0].text()).toBe('最新优先')
      expect(radioButtons[1].text()).toBe('最早优先')
    })
  })

  describe('Config List Display', () => {
    it('displays config list when configs are available', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.displayedConfigs).toHaveLength(3)
    })

    it('displays empty state when no configs', async () => {
      wrapper = await createWrapper([])
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.find('.el-empty').exists()).toBe(true)
    })

    it('displays correct session types', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      const configs = wrapper.vm.displayedConfigs
      expect(configs.filter(c => c.session_type === 'user')).toHaveLength(2)
      expect(configs.filter(c => c.session_type === 'group')).toHaveLength(1)
    })
  })

  describe('Search Functionality', () => {
    it('filters configs by session_id search term', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      // Set search query
      wrapper.vm.searchQuery = 'user'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed).toHaveLength(2)
      expect(displayed.every(c => c.session_id.includes('user'))).toBe(true)
    })

    it('search is case insensitive', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.searchQuery = 'USER'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed).toHaveLength(2)
    })

    it('shows all configs when search is cleared', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.searchQuery = 'user'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.displayedConfigs).toHaveLength(2)
      
      wrapper.vm.searchQuery = ''
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.displayedConfigs).toHaveLength(3)
    })

    it('returns empty array when no matches found', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.searchQuery = 'nonexistent'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.displayedConfigs).toHaveLength(0)
    })
  })

  describe('Filter Functionality', () => {
    it('filters configs by session type - user', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.filterType = 'user'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed).toHaveLength(2)
      expect(displayed.every(c => c.session_type === 'user')).toBe(true)
    })

    it('filters configs by session type - group', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.filterType = 'group'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed).toHaveLength(1)
      expect(displayed[0].session_type).toBe('group')
    })

    it('shows all configs when filter is cleared', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.filterType = 'user'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.displayedConfigs).toHaveLength(2)
      
      wrapper.vm.filterType = ''
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.displayedConfigs).toHaveLength(3)
    })

    it('combines search and filter correctly', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.searchQuery = '001'
      wrapper.vm.filterType = 'user'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed).toHaveLength(1)
      expect(displayed[0].session_id).toBe('user_001')
    })
  })

  describe('Sort Functionality', () => {
    it('sorts configs by update time descending (newest first)', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.sortOrder = 'desc'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed[0].session_id).toBe('user_001') // 2024-01-03
      expect(displayed[1].session_id).toBe('group_001') // 2024-01-02
      expect(displayed[2].session_id).toBe('user_002') // 2024-01-01
    })

    it('sorts configs by update time ascending (oldest first)', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.sortOrder = 'asc'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed[0].session_id).toBe('user_002') // 2024-01-01
      expect(displayed[1].session_id).toBe('group_001') // 2024-01-02
      expect(displayed[2].session_id).toBe('user_001') // 2024-01-03
    })

    it('maintains sort order when filtering', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.sortOrder = 'desc'
      wrapper.vm.filterType = 'user'
      await wrapper.vm.$nextTick()
      
      const displayed = wrapper.vm.displayedConfigs
      expect(displayed).toHaveLength(2)
      expect(displayed[0].session_id).toBe('user_001')
      expect(displayed[1].session_id).toBe('user_002')
    })
  })

  describe('Refresh Functionality', () => {
    it('calls fetchConfigs when refresh button is clicked', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const fetchSpy = vi.spyOn(configStore, 'fetchConfigs').mockResolvedValue([])
      
      await wrapper.vm.handleRefresh()
      await flushPromises()
      
      expect(fetchSpy).toHaveBeenCalled()
    })

    it('shows success message after refresh', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      vi.spyOn(configStore, 'fetchConfigs').mockResolvedValue([])
      
      await wrapper.vm.handleRefresh()
      await flushPromises()
      
      expect(ElMessage.success).toHaveBeenCalledWith('刷新成功')
    })

    it('shows error message when refresh fails', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const error = new Error('Network error')
      error.userMessage = '加载配置列表失败'
      vi.spyOn(configStore, 'fetchConfigs').mockRejectedValue(error)
      
      await wrapper.vm.handleRefresh()
      await flushPromises()
      
      expect(ElMessage.error).toHaveBeenCalledWith('加载配置列表失败')
    })

    it('sets loading state during refresh', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      let resolveRefresh
      const refreshPromise = new Promise(resolve => {
        resolveRefresh = resolve
      })
      vi.spyOn(configStore, 'fetchConfigs').mockReturnValue(refreshPromise)
      
      const refreshPromiseCall = wrapper.vm.handleRefresh()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.loading).toBe(true)
      
      resolveRefresh([])
      await refreshPromiseCall
      await flushPromises()
      
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Export Functionality', () => {
    it('calls exportConfigs when export button is clicked', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const exportSpy = vi.spyOn(configStore, 'exportConfigs').mockResolvedValue()
      
      await wrapper.vm.handleExport()
      await flushPromises()
      
      expect(exportSpy).toHaveBeenCalled()
    })

    it('shows success message after export', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      vi.spyOn(configStore, 'exportConfigs').mockResolvedValue()
      
      await wrapper.vm.handleExport()
      await flushPromises()
      
      expect(ElMessage.success).toHaveBeenCalledWith('配置导出成功')
    })

    it('shows error message when export fails', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const error = new Error('Export failed')
      error.userMessage = '导出配置失败'
      vi.spyOn(configStore, 'exportConfigs').mockRejectedValue(error)
      
      await wrapper.vm.handleExport()
      await flushPromises()
      
      expect(ElMessage.error).toHaveBeenCalledWith('导出配置失败')
    })

    it('sets exporting state during export', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      let resolveExport
      const exportPromise = new Promise(resolve => {
        resolveExport = resolve
      })
      vi.spyOn(configStore, 'exportConfigs').mockReturnValue(exportPromise)
      
      const exportPromiseCall = wrapper.vm.handleExport()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.exporting).toBe(true)
      
      resolveExport()
      await exportPromiseCall
      await flushPromises()
      
      expect(wrapper.vm.exporting).toBe(false)
    })
  })

  describe('Import Functionality', () => {
    it('triggers file input click when import button is clicked', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const fileInput = { click: vi.fn() }
      wrapper.vm.fileInput = fileInput
      
      wrapper.vm.handleImportClick()
      
      expect(fileInput.click).toHaveBeenCalled()
    })

    it('imports file and shows success message', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const mockFile = new File(['{"configs":[]}'], 'configs.json', { type: 'application/json' })
      const mockResult = { imported_count: 5 }
      
      vi.spyOn(configStore, 'importConfigs').mockResolvedValue(mockResult)
      
      const event = {
        target: {
          files: [mockFile],
          value: 'configs.json'
        }
      }
      
      await wrapper.vm.handleImportFile(event)
      await flushPromises()
      
      expect(configStore.importConfigs).toHaveBeenCalledWith(mockFile)
      expect(ElMessage.success).toHaveBeenCalledWith('成功导入 5 个配置')
      expect(event.target.value).toBe('')
    })

    it('shows error message when import fails', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const mockFile = new File(['invalid'], 'configs.json')
      const error = new Error('Invalid format')
      error.userMessage = '导入配置失败'
      
      vi.spyOn(configStore, 'importConfigs').mockRejectedValue(error)
      
      const event = {
        target: {
          files: [mockFile],
          value: 'configs.json'
        }
      }
      
      await wrapper.vm.handleImportFile(event)
      await flushPromises()
      
      expect(ElMessage.error).toHaveBeenCalledWith('导入配置失败')
      expect(event.target.value).toBe('')
    })

    it('does nothing when no file is selected', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const importSpy = vi.spyOn(configStore, 'importConfigs')
      
      const event = {
        target: {
          files: []
        }
      }
      
      await wrapper.vm.handleImportFile(event)
      
      expect(importSpy).not.toHaveBeenCalled()
    })
  })

  describe('Navigation', () => {
    it('navigates to detail page when row is clicked', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const routerPushSpy = vi.spyOn(router, 'push')
      
      const row = mockConfigs[0]
      wrapper.vm.handleRowClick(row)
      
      expect(routerPushSpy).toHaveBeenCalledWith('/configs/user_001')
    })

    it('navigates to detail page when view button is clicked', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const routerPushSpy = vi.spyOn(router, 'push')
      
      wrapper.vm.handleViewDetail('group_001')
      
      expect(routerPushSpy).toHaveBeenCalledWith('/configs/group_001')
    })
  })

  describe('Time Formatting', () => {
    it('formats recent time as "刚刚"', () => {
      wrapper = mount(ConfigList, {
        global: {
          plugins: [router, pinia],
          stubs: { 'el-button': true, 'el-card': true, 'el-input': true, 'el-select': true, 'el-option': true, 'el-radio-group': true, 'el-radio-button': true, 'el-table': true, 'el-table-column': true, 'el-tag': true, 'el-icon': true, 'el-empty': true }
        }
      })
      
      const now = new Date()
      const result = wrapper.vm.formatTime(now.toISOString())
      expect(result).toBe('刚刚')
    })

    it('formats time within 1 hour as minutes ago', () => {
      wrapper = mount(ConfigList, {
        global: {
          plugins: [router, pinia],
          stubs: { 'el-button': true, 'el-card': true, 'el-input': true, 'el-select': true, 'el-option': true, 'el-radio-group': true, 'el-radio-button': true, 'el-table': true, 'el-table-column': true, 'el-tag': true, 'el-icon': true, 'el-empty': true }
        }
      })
      
      const now = new Date()
      const past = new Date(now.getTime() - 30 * 60 * 1000) // 30 minutes ago
      const result = wrapper.vm.formatTime(past.toISOString())
      expect(result).toBe('30 分钟前')
    })

    it('formats time within 1 day as hours ago', () => {
      wrapper = mount(ConfigList, {
        global: {
          plugins: [router, pinia],
          stubs: { 'el-button': true, 'el-card': true, 'el-input': true, 'el-select': true, 'el-option': true, 'el-radio-group': true, 'el-radio-button': true, 'el-table': true, 'el-table-column': true, 'el-tag': true, 'el-icon': true, 'el-empty': true }
        }
      })
      
      const now = new Date()
      const past = new Date(now.getTime() - 5 * 60 * 60 * 1000) // 5 hours ago
      const result = wrapper.vm.formatTime(past.toISOString())
      expect(result).toBe('5 小时前')
    })

    it('formats time within 7 days as days ago', () => {
      wrapper = mount(ConfigList, {
        global: {
          plugins: [router, pinia],
          stubs: { 'el-button': true, 'el-card': true, 'el-input': true, 'el-select': true, 'el-option': true, 'el-radio-group': true, 'el-radio-button': true, 'el-table': true, 'el-table-column': true, 'el-tag': true, 'el-icon': true, 'el-empty': true }
        }
      })
      
      const now = new Date()
      const past = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000) // 3 days ago
      const result = wrapper.vm.formatTime(past.toISOString())
      expect(result).toBe('3 天前')
    })

    it('formats old time as full date', () => {
      wrapper = mount(ConfigList, {
        global: {
          plugins: [router, pinia],
          stubs: { 'el-button': true, 'el-card': true, 'el-input': true, 'el-select': true, 'el-option': true, 'el-radio-group': true, 'el-radio-button': true, 'el-table': true, 'el-table-column': true, 'el-tag': true, 'el-icon': true, 'el-empty': true }
        }
      })
      
      const past = new Date('2024-01-01T10:00:00Z')
      const result = wrapper.vm.formatTime(past.toISOString())
      expect(result).toMatch(/2024/)
    })

    it('returns "-" for null timestamp', () => {
      wrapper = mount(ConfigList, {
        global: {
          plugins: [router, pinia],
          stubs: { 'el-button': true, 'el-card': true, 'el-input': true, 'el-select': true, 'el-option': true, 'el-radio-group': true, 'el-radio-button': true, 'el-table': true, 'el-table-column': true, 'el-tag': true, 'el-icon': true, 'el-empty': true }
        }
      })
      
      const result = wrapper.vm.formatTime(null)
      expect(result).toBe('-')
    })
  })

  describe('Loading State', () => {
    it('shows loading state when fetching configs', async () => {
      wrapper = await createWrapper([])
      
      let resolveFetch
      const fetchPromise = new Promise(resolve => {
        resolveFetch = resolve
      })
      vi.spyOn(configStore, 'fetchConfigs').mockReturnValue(fetchPromise)
      
      const loadPromise = wrapper.vm.loadConfigs()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.loading).toBe(true)
      
      resolveFetch([])
      await loadPromise
      await flushPromises()
      
      expect(wrapper.vm.loading).toBe(false)
    })

    it('clears loading state after fetch error', async () => {
      wrapper = await createWrapper([])
      
      const error = new Error('Network error')
      error.userMessage = '加载失败'
      vi.spyOn(configStore, 'fetchConfigs').mockRejectedValue(error)
      
      await wrapper.vm.loadConfigs()
      await flushPromises()
      
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Empty State', () => {
    it('shows empty state when no configs are available', async () => {
      wrapper = await createWrapper([])
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.displayedConfigs).toHaveLength(0)
      expect(wrapper.find('.empty-state').exists()).toBe(true)
    })

    it('shows empty state when search returns no results', async () => {
      wrapper = await createWrapper(mockConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.searchQuery = 'nonexistent'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.displayedConfigs).toHaveLength(0)
    })

    it('shows empty state when filter returns no results', async () => {
      const userOnlyConfigs = [mockConfigs[0], mockConfigs[2]]
      wrapper = await createWrapper(userOnlyConfigs)
      await wrapper.vm.$nextTick()
      
      wrapper.vm.filterType = 'group'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.displayedConfigs).toHaveLength(0)
    })

    it('hides empty state when configs are loaded', async () => {
      wrapper = await createWrapper([])
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      
      configStore.configs = mockConfigs
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.displayedConfigs).toHaveLength(3)
    })
  })

  describe('Lifecycle', () => {
    it('loads configs on mount', async () => {
      const fetchSpy = vi.spyOn(useConfigStore(), 'fetchConfigs').mockResolvedValue([])
      
      wrapper = await createWrapper([])
      await flushPromises()
      
      expect(fetchSpy).toHaveBeenCalled()
    })
  })

  describe('Row Class Name', () => {
    it('returns clickable-row class for all rows', async () => {
      wrapper = await createWrapper(mockConfigs)
      
      const className = wrapper.vm.getRowClassName()
      expect(className).toBe('clickable-row')
    })
  })
})
