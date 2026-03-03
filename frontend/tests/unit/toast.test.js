import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ElMessage } from 'element-plus'
import {
  showSuccess,
  showError,
  showWarning,
  showInfo,
  showApiError,
  showNetworkError,
  showValidationError
} from '@/utils/toast'

// Mock Element Plus ElMessage
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

describe('Toast Utility', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('showSuccess', () => {
    it('calls ElMessage.success with correct parameters', () => {
      const message = '操作成功'
      showSuccess(message)
      
      expect(ElMessage.success).toHaveBeenCalledWith({
        message,
        duration: 3000,
        showClose: true,
        grouping: true
      })
    })

    it('accepts custom duration', () => {
      const message = '操作成功'
      const customDuration = 5000
      showSuccess(message, customDuration)
      
      expect(ElMessage.success).toHaveBeenCalledWith({
        message,
        duration: customDuration,
        showClose: true,
        grouping: true
      })
    })
  })

  describe('showError', () => {
    it('calls ElMessage.error with correct parameters', () => {
      const message = '操作失败'
      showError(message)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message,
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })

    it('accepts custom duration', () => {
      const message = '操作失败'
      const customDuration = 10000
      showError(message, customDuration)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message,
        duration: customDuration,
        showClose: true,
        grouping: true
      })
    })
  })

  describe('showWarning', () => {
    it('calls ElMessage.warning with correct parameters', () => {
      const message = '警告信息'
      showWarning(message)
      
      expect(ElMessage.warning).toHaveBeenCalledWith({
        message,
        duration: 4000,
        showClose: true,
        grouping: true
      })
    })

    it('accepts custom duration', () => {
      const message = '警告信息'
      const customDuration = 6000
      showWarning(message, customDuration)
      
      expect(ElMessage.warning).toHaveBeenCalledWith({
        message,
        duration: customDuration,
        showClose: true,
        grouping: true
      })
    })
  })

  describe('showInfo', () => {
    it('calls ElMessage.info with correct parameters', () => {
      const message = '提示信息'
      showInfo(message)
      
      expect(ElMessage.info).toHaveBeenCalledWith({
        message,
        duration: 3000,
        showClose: true,
        grouping: true
      })
    })

    it('accepts custom duration', () => {
      const message = '提示信息'
      const customDuration = 4000
      showInfo(message, customDuration)
      
      expect(ElMessage.info).toHaveBeenCalledWith({
        message,
        duration: customDuration,
        showClose: true,
        grouping: true
      })
    })
  })

  describe('showApiError', () => {
    it('shows error with userMessage from error object', () => {
      const error = {
        userMessage: '自定义错误消息'
      }
      showApiError(error)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message: '自定义错误消息',
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })

    it('falls back to error.message if userMessage is not available', () => {
      const error = {
        message: '标准错误消息'
      }
      showApiError(error)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message: '标准错误消息',
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })

    it('uses fallback message if error has no message', () => {
      const error = {}
      const fallbackMessage = '自定义回退消息'
      showApiError(error, fallbackMessage)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message: fallbackMessage,
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })

    it('uses default fallback message if none provided', () => {
      const error = {}
      showApiError(error)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message: '操作失败',
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })

    it('handles null error gracefully', () => {
      showApiError(null)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message: '操作失败',
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })
  })

  describe('showNetworkError', () => {
    it('shows network error message', () => {
      showNetworkError()
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message: '网络连接失败，请检查网络连接',
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })
  })

  describe('showValidationError', () => {
    it('shows validation error with custom message', () => {
      const message = '表单验证失败'
      showValidationError(message)
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message,
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })

    it('shows default validation error message', () => {
      showValidationError()
      
      expect(ElMessage.error).toHaveBeenCalledWith({
        message: '请检查输入的数据是否正确',
        duration: 5000,
        showClose: true,
        grouping: true
      })
    })
  })

  describe('Default Export', () => {
    it('exports all methods as default object', async () => {
      const toast = await import('@/utils/toast')
      
      expect(toast.default).toBeDefined()
      expect(toast.default.success).toBe(showSuccess)
      expect(toast.default.error).toBe(showError)
      expect(toast.default.warning).toBe(showWarning)
      expect(toast.default.info).toBe(showInfo)
      expect(toast.default.apiError).toBe(showApiError)
      expect(toast.default.networkError).toBe(showNetworkError)
      expect(toast.default.validationError).toBe(showValidationError)
    })
  })
})
