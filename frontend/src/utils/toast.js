import { ElMessage } from 'element-plus'

/**
 * Toast notification utility
 * Provides standardized toast notifications with consistent timing and styling
 */

// Default durations (in milliseconds)
const DURATIONS = {
  success: 3000,  // 3 seconds
  error: 5000,    // 5 seconds
  warning: 4000,  // 4 seconds
  info: 3000      // 3 seconds
}

/**
 * Show success toast
 * @param {string} message - Success message to display
 * @param {number} duration - Optional custom duration in milliseconds
 */
export function showSuccess(message, duration = DURATIONS.success) {
  ElMessage.success({
    message,
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show error toast
 * @param {string} message - Error message to display
 * @param {number} duration - Optional custom duration in milliseconds
 */
export function showError(message, duration = DURATIONS.error) {
  ElMessage.error({
    message,
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show warning toast
 * @param {string} message - Warning message to display
 * @param {number} duration - Optional custom duration in milliseconds
 */
export function showWarning(message, duration = DURATIONS.warning) {
  ElMessage.warning({
    message,
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show info toast
 * @param {string} message - Info message to display
 * @param {number} duration - Optional custom duration in milliseconds
 */
export function showInfo(message, duration = DURATIONS.info) {
  ElMessage.info({
    message,
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show API error toast with appropriate message
 * Extracts user-friendly message from error object
 * @param {Error} error - Error object from API call
 * @param {string} fallbackMessage - Fallback message if error doesn't have userMessage
 */
export function showApiError(error, fallbackMessage = '操作失败') {
  const message = error?.userMessage || error?.message || fallbackMessage
  showError(message)
}

/**
 * Show network error toast
 */
export function showNetworkError() {
  showError('网络连接失败，请检查网络连接')
}

/**
 * Show validation error toast
 * @param {string} message - Validation error message
 */
export function showValidationError(message = '请检查输入的数据是否正确') {
  showError(message)
}

// Export default object with all methods
export default {
  success: showSuccess,
  error: showError,
  warning: showWarning,
  info: showInfo,
  apiError: showApiError,
  networkError: showNetworkError,
  validationError: showValidationError
}
