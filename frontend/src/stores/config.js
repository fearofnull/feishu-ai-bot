import { defineStore } from 'pinia'
import { configAPI } from '@/api/client'

export const useConfigStore = defineStore('config', {
  state: () => ({
    configs: [],
    currentConfig: null,
    globalConfig: null,
    loading: false,
    error: null
  }),
  
  getters: {
    // Get configs filtered by session type
    configsByType: (state) => (sessionType) => {
      if (!sessionType) return state.configs
      return state.configs.filter(config => config.session_type === sessionType)
    },
    
    // Search configs by session_id
    searchConfigs: (state) => (searchTerm) => {
      if (!searchTerm) return state.configs
      const term = searchTerm.toLowerCase()
      return state.configs.filter(config => 
        config.session_id.toLowerCase().includes(term)
      )
    },
    
    // Get sorted configs by update time
    sortedConfigs: (state) => (order = 'desc') => {
      const sorted = [...state.configs].sort((a, b) => {
        const timeA = new Date(a.metadata?.updated_at || a.metadata?.created_at)
        const timeB = new Date(b.metadata?.updated_at || b.metadata?.created_at)
        return order === 'desc' ? timeB - timeA : timeA - timeB
      })
      return sorted
    }
  },
  
  actions: {
    async fetchConfigs(filters = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await configAPI.getConfigs(filters)
        this.configs = response.data.data || []
        return this.configs
      } catch (error) {
        this.error = error.userMessage || '获取配置列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchConfig(sessionId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await configAPI.getConfig(sessionId)
        this.currentConfig = response.data.data
        return this.currentConfig
      } catch (error) {
        this.error = error.userMessage || '获取配置详情失败'
        this.currentConfig = null
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchEffectiveConfig(sessionId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await configAPI.getEffectiveConfig(sessionId)
        return response.data.data
      } catch (error) {
        this.error = error.userMessage || '获取有效配置失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchGlobalConfig() {
      this.loading = true
      this.error = null
      
      try {
        const response = await configAPI.getGlobalConfig()
        // API returns { data: { global_config: {...} } }
        this.globalConfig = response.data.data.global_config
        return this.globalConfig
      } catch (error) {
        this.error = error.userMessage || '获取全局配置失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateConfig(sessionId, data) {
      this.loading = true
      this.error = null
      
      try {
        const response = await configAPI.updateConfig(sessionId, data)
        const updatedConfig = response.data.data
        
        // Update in configs list if exists
        const index = this.configs.findIndex(c => c.session_id === sessionId)
        if (index !== -1) {
          this.configs[index] = updatedConfig
        } else {
          // Add new config to list
          this.configs.push(updatedConfig)
        }
        
        // Update current config if it's the same session
        if (this.currentConfig?.session_id === sessionId) {
          this.currentConfig = updatedConfig
        }
        
        return updatedConfig
      } catch (error) {
        this.error = error.userMessage || '更新配置失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteConfig(sessionId) {
      this.loading = true
      this.error = null
      
      try {
        await configAPI.deleteConfig(sessionId)
        
        // Remove from configs list
        this.configs = this.configs.filter(c => c.session_id !== sessionId)
        
        // Clear current config if it's the deleted one
        if (this.currentConfig?.session_id === sessionId) {
          this.currentConfig = null
        }
        
        return true
      } catch (error) {
        this.error = error.userMessage || '删除配置失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async exportConfigs() {
      this.loading = true
      this.error = null
      
      try {
        const response = await configAPI.exportConfigs()
        
        // Create download link for the blob
        const blob = new Blob([response.data], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Generate filename with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
        link.download = `configs-export-${timestamp}.json`
        
        // Trigger download
        document.body.appendChild(link)
        link.click()
        
        // Cleanup
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        return true
      } catch (error) {
        this.error = error.userMessage || '导出配置失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async importConfigs(file) {
      this.loading = true
      this.error = null
      
      try {
        const response = await configAPI.importConfigs(file)
        const result = response.data.data
        
        // Refresh configs list after import
        await this.fetchConfigs()
        
        return result
      } catch (error) {
        this.error = error.userMessage || '导入配置失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Clear current config
    clearCurrentConfig() {
      this.currentConfig = null
    },
    
    // Clear error
    clearError() {
      this.error = null
    }
  }
})
