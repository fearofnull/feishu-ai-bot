import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useConfigStore } from '@/stores/config'
import { configAPI } from '@/api/client'

// Mock the API client
vi.mock('@/api/client', () => ({
  configAPI: {
    getConfigs: vi.fn(),
    getConfig: vi.fn(),
    getEffectiveConfig: vi.fn(),
    updateConfig: vi.fn(),
    deleteConfig: vi.fn(),
    getGlobalConfig: vi.fn(),
    exportConfigs: vi.fn(),
    importConfigs: vi.fn()
  }
}))

describe('Config Store', () => {
  let store

  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia())
    store = useConfigStore()
    
    // Clear all mocks
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have empty configs array', () => {
      expect(store.configs).toEqual([])
    })

    it('should have null currentConfig', () => {
      expect(store.currentConfig).toBeNull()
    })

    it('should have null globalConfig', () => {
      expect(store.globalConfig).toBeNull()
    })

    it('should have loading false', () => {
      expect(store.loading).toBe(false)
    })

    it('should have null error', () => {
      expect(store.error).toBeNull()
    })
  })

  describe('Getters', () => {
    beforeEach(() => {
      store.configs = [
        { session_id: 'user1', session_type: 'user', chat_name: null, metadata: { updated_at: '2024-01-01T10:00:00Z' } },
        { session_id: 'group1', session_type: 'group', chat_name: '开发团队', metadata: { updated_at: '2024-01-02T10:00:00Z' } },
        { session_id: 'user2', session_type: 'user', chat_name: null, metadata: { updated_at: '2024-01-03T10:00:00Z' } }
      ]
    })

    it('configsByType should filter by session type', () => {
      const userConfigs = store.configsByType('user')
      expect(userConfigs).toHaveLength(2)
      expect(userConfigs.every(c => c.session_type === 'user')).toBe(true)
    })

    it('configsByType should return all configs when no type specified', () => {
      const allConfigs = store.configsByType(null)
      expect(allConfigs).toHaveLength(3)
    })

    it('searchConfigs should filter by session_id', () => {
      const results = store.searchConfigs('user')
      expect(results).toHaveLength(2)
      expect(results.every(c => c.session_id.includes('user'))).toBe(true)
    })

    it('searchConfigs should filter by chat_name', () => {
      const results = store.searchConfigs('开发')
      expect(results).toHaveLength(1)
      expect(results[0].chat_name).toBe('开发团队')
    })

    it('searchConfigs should be case insensitive', () => {
      const results = store.searchConfigs('USER')
      expect(results).toHaveLength(2)
    })

    it('searchConfigs should return all configs when no search term', () => {
      const results = store.searchConfigs('')
      expect(results).toHaveLength(3)
    })

    it('searchConfigs should search across both session_id and chat_name', () => {
      let results = store.searchConfigs('group1')
      expect(results).toHaveLength(1)
      
      results = store.searchConfigs('开发团队')
      expect(results).toHaveLength(1)
    })

    it('sortedConfigs should sort by update time descending', () => {
      const sorted = store.sortedConfigs('desc')
      expect(sorted[0].session_id).toBe('user2')
      expect(sorted[2].session_id).toBe('user1')
    })

    it('sortedConfigs should sort by update time ascending', () => {
      const sorted = store.sortedConfigs('asc')
      expect(sorted[0].session_id).toBe('user1')
      expect(sorted[2].session_id).toBe('user2')
    })
  })

  describe('fetchConfigs', () => {
    it('should fetch configs successfully', async () => {
      const mockConfigs = [
        { session_id: 'test1', session_type: 'user' },
        { session_id: 'test2', session_type: 'group' }
      ]
      
      configAPI.getConfigs.mockResolvedValue({
        data: { data: mockConfigs }
      })

      const result = await store.fetchConfigs()

      expect(configAPI.getConfigs).toHaveBeenCalledWith({})
      expect(store.configs).toEqual(mockConfigs)
      expect(result).toEqual(mockConfigs)
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should pass filters to API', async () => {
      configAPI.getConfigs.mockResolvedValue({
        data: { data: [] }
      })

      await store.fetchConfigs({ session_type: 'user' })

      expect(configAPI.getConfigs).toHaveBeenCalledWith({ session_type: 'user' })
    })

    it('should handle fetch error', async () => {
      const error = new Error('Network error')
      error.userMessage = '获取配置列表失败'
      configAPI.getConfigs.mockRejectedValue(error)

      await expect(store.fetchConfigs()).rejects.toThrow()
      expect(store.error).toBe('获取配置列表失败')
      expect(store.loading).toBe(false)
    })

    it('should set loading state during fetch', async () => {
      configAPI.getConfigs.mockImplementation(() => {
        expect(store.loading).toBe(true)
        return Promise.resolve({ data: { data: [] } })
      })

      await store.fetchConfigs()
    })
  })

  describe('fetchConfig', () => {
    it('should fetch single config successfully', async () => {
      const mockConfig = {
        session_id: 'test1',
        session_type: 'user',
        config: { default_provider: 'claude' }
      }
      
      configAPI.getConfig.mockResolvedValue({
        data: { data: mockConfig }
      })

      const result = await store.fetchConfig('test1')

      expect(configAPI.getConfig).toHaveBeenCalledWith('test1')
      expect(store.currentConfig).toEqual(mockConfig)
      expect(result).toEqual(mockConfig)
    })

    it('should handle config not found', async () => {
      const error = new Error('Not found')
      error.userMessage = '配置不存在'
      configAPI.getConfig.mockRejectedValue(error)

      await expect(store.fetchConfig('nonexistent')).rejects.toThrow()
      expect(store.currentConfig).toBeNull()
      expect(store.error).toBe('配置不存在')
    })
  })

  describe('fetchEffectiveConfig', () => {
    it('should fetch effective config successfully', async () => {
      const mockEffectiveConfig = {
        target_project_dir: '/path/to/project',
        default_provider: 'claude'
      }
      
      configAPI.getEffectiveConfig.mockResolvedValue({
        data: { data: mockEffectiveConfig }
      })

      const result = await store.fetchEffectiveConfig('test1')

      expect(configAPI.getEffectiveConfig).toHaveBeenCalledWith('test1')
      expect(result).toEqual(mockEffectiveConfig)
    })
  })

  describe('fetchGlobalConfig', () => {
    it('should fetch global config successfully', async () => {
      const mockGlobalConfig = {
        target_project_dir: '/default/path',
        default_provider: 'claude'
      }
      
      configAPI.getGlobalConfig.mockResolvedValue({
        data: { data: mockGlobalConfig }
      })

      const result = await store.fetchGlobalConfig()

      expect(configAPI.getGlobalConfig).toHaveBeenCalled()
      expect(store.globalConfig).toEqual(mockGlobalConfig)
      expect(result).toEqual(mockGlobalConfig)
    })
  })

  describe('updateConfig', () => {
    it('should update existing config in list', async () => {
      store.configs = [
        { session_id: 'test1', config: { default_provider: 'claude' } }
      ]

      const updatedConfig = {
        session_id: 'test1',
        config: { default_provider: 'gemini' }
      }

      configAPI.updateConfig.mockResolvedValue({
        data: { data: updatedConfig }
      })

      const result = await store.updateConfig('test1', { default_provider: 'gemini' })

      expect(configAPI.updateConfig).toHaveBeenCalledWith('test1', { default_provider: 'gemini' })
      expect(store.configs[0]).toEqual(updatedConfig)
      expect(result).toEqual(updatedConfig)
    })

    it('should add new config to list if not exists', async () => {
      store.configs = []

      const newConfig = {
        session_id: 'test1',
        config: { default_provider: 'claude' }
      }

      configAPI.updateConfig.mockResolvedValue({
        data: { data: newConfig }
      })

      await store.updateConfig('test1', { default_provider: 'claude' })

      expect(store.configs).toHaveLength(1)
      expect(store.configs[0]).toEqual(newConfig)
    })

    it('should update currentConfig if same session', async () => {
      store.currentConfig = {
        session_id: 'test1',
        config: { default_provider: 'claude' }
      }

      const updatedConfig = {
        session_id: 'test1',
        config: { default_provider: 'gemini' }
      }

      configAPI.updateConfig.mockResolvedValue({
        data: { data: updatedConfig }
      })

      await store.updateConfig('test1', { default_provider: 'gemini' })

      expect(store.currentConfig).toEqual(updatedConfig)
    })

    it('should handle update error', async () => {
      const error = new Error('Validation error')
      error.userMessage = '配置值无效'
      configAPI.updateConfig.mockRejectedValue(error)

      await expect(store.updateConfig('test1', {})).rejects.toThrow()
      expect(store.error).toBe('配置值无效')
    })
  })

  describe('deleteConfig', () => {
    it('should delete config from list', async () => {
      store.configs = [
        { session_id: 'test1' },
        { session_id: 'test2' }
      ]

      configAPI.deleteConfig.mockResolvedValue({})

      await store.deleteConfig('test1')

      expect(configAPI.deleteConfig).toHaveBeenCalledWith('test1')
      expect(store.configs).toHaveLength(1)
      expect(store.configs[0].session_id).toBe('test2')
    })

    it('should clear currentConfig if deleted', async () => {
      store.currentConfig = { session_id: 'test1' }
      configAPI.deleteConfig.mockResolvedValue({})

      await store.deleteConfig('test1')

      expect(store.currentConfig).toBeNull()
    })

    it('should handle delete error', async () => {
      const error = new Error('Delete failed')
      error.userMessage = '删除配置失败'
      configAPI.deleteConfig.mockRejectedValue(error)

      await expect(store.deleteConfig('test1')).rejects.toThrow()
      expect(store.error).toBe('删除配置失败')
    })
  })

  describe('exportConfigs', () => {
    it('should export configs and trigger download', async () => {
      const mockBlob = new Blob(['{"configs":[]}'], { type: 'application/json' })
      
      configAPI.exportConfigs.mockResolvedValue({
        data: mockBlob
      })

      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
        parentNode: null
      }
      
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink)
      const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => {})
      const removeChildSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => {})
      const createObjectURLSpy = vi.spyOn(window.URL, 'createObjectURL').mockReturnValue('blob:mock-url')
      const revokeObjectURLSpy = vi.spyOn(window.URL, 'revokeObjectURL').mockImplementation(() => {})

      await store.exportConfigs()

      expect(configAPI.exportConfigs).toHaveBeenCalled()
      expect(createObjectURLSpy).toHaveBeenCalled()
      expect(mockLink.click).toHaveBeenCalled()
      expect(appendChildSpy).toHaveBeenCalledWith(mockLink)
      expect(removeChildSpy).toHaveBeenCalledWith(mockLink)
      expect(revokeObjectURLSpy).toHaveBeenCalled()
      expect(mockLink.download).toMatch(/^configs-export-.*\.json$/)

      // Cleanup
      createElementSpy.mockRestore()
      appendChildSpy.mockRestore()
      removeChildSpy.mockRestore()
      createObjectURLSpy.mockRestore()
      revokeObjectURLSpy.mockRestore()
    })

    it('should handle export error', async () => {
      const error = new Error('Export failed')
      error.userMessage = '导出配置失败'
      configAPI.exportConfigs.mockRejectedValue(error)

      await expect(store.exportConfigs()).rejects.toThrow()
      expect(store.error).toBe('导出配置失败')
    })
  })

  describe('importConfigs', () => {
    it('should import configs and refresh list', async () => {
      const mockFile = new File(['{"configs":[]}'], 'configs.json', { type: 'application/json' })
      const mockResult = { imported_count: 5 }

      configAPI.importConfigs.mockResolvedValue({
        data: { data: mockResult }
      })

      configAPI.getConfigs.mockResolvedValue({
        data: { data: [] }
      })

      const result = await store.importConfigs(mockFile)

      expect(configAPI.importConfigs).toHaveBeenCalledWith(mockFile)
      expect(configAPI.getConfigs).toHaveBeenCalled()
      expect(result).toEqual(mockResult)
    })

    it('should handle import error', async () => {
      const mockFile = new File(['invalid'], 'configs.json')
      const error = new Error('Invalid format')
      error.userMessage = '导入文件格式无效'
      configAPI.importConfigs.mockRejectedValue(error)

      await expect(store.importConfigs(mockFile)).rejects.toThrow()
      expect(store.error).toBe('导入文件格式无效')
    })
  })

  describe('Utility Actions', () => {
    it('clearCurrentConfig should clear current config', () => {
      store.currentConfig = { session_id: 'test1' }
      store.clearCurrentConfig()
      expect(store.currentConfig).toBeNull()
    })

    it('clearError should clear error', () => {
      store.error = 'Some error'
      store.clearError()
      expect(store.error).toBeNull()
    })
  })
})
