# API Client Documentation

## Overview

The API client (`client.js`) provides a robust Axios-based HTTP client for communicating with the backend API. It includes automatic token management, comprehensive error handling, and convenient API helper functions.

## Features

### 1. Base Configuration
- **Base URL**: Configurable via `VITE_API_BASE_URL` environment variable (defaults to `/api`)
- **Timeout**: 10 seconds
- **Content-Type**: `application/json`

### 2. Request Interceptor
Automatically adds JWT token from localStorage to all requests:
```javascript
Authorization: Bearer <token>
```

### 3. Response Interceptor
Handles common HTTP errors and provides user-friendly error messages:

| Status Code | User Message | Action |
|-------------|--------------|--------|
| 401 | 登录已过期，请重新登录 | Clears token, redirects to login |
| 403 | 没有权限执行此操作 | - |
| 404 | 请求的资源不存在 | - |
| 400 | 请求参数无效 | Includes validation errors |
| 500 | 服务器内部错误，请稍后重试 | - |
| Network Error | 网络连接失败，请检查网络连接 | - |

### 4. Error Object Enhancement
All errors are enhanced with a `userMessage` property for display to users:
```javascript
try {
  await apiClient.get('/configs')
} catch (error) {
  console.error(error.userMessage) // User-friendly message
}
```

## API Helper Functions

### Auth API
```javascript
import { authAPI } from '@/api/client'

// Login
const response = await authAPI.login('password')
// Returns: { data: { token, expires_in } }

// Logout
await authAPI.logout()
```

### Config API
```javascript
import { configAPI } from '@/api/client'

// Get all configs (with optional filters)
const configs = await configAPI.getConfigs({ 
  session_type: 'user',
  search: 'ou_123'
})

// Get single config
const config = await configAPI.getConfig('session_id')

// Get effective config (with defaults applied)
const effectiveConfig = await configAPI.getEffectiveConfig('session_id')

// Update config
await configAPI.updateConfig('session_id', {
  default_provider: 'claude',
  default_layer: 'api'
})

// Delete config (reset to defaults)
await configAPI.deleteConfig('session_id')

// Get global config
const globalConfig = await configAPI.getGlobalConfig()

// Export all configs (returns blob)
const blob = await configAPI.exportConfigs()

// Import configs from file
await configAPI.importConfigs(file)
```

## Usage in Stores

The API client is designed to be used in Pinia stores:

```javascript
import { defineStore } from 'pinia'
import { configAPI } from '@/api/client'

export const useConfigStore = defineStore('config', {
  state: () => ({
    configs: []
  }),
  
  actions: {
    async fetchConfigs() {
      try {
        const response = await configAPI.getConfigs()
        this.configs = response.data.data
      } catch (error) {
        // error.userMessage is available for display
        console.error(error.userMessage)
        throw error
      }
    }
  }
})
```

## Error Handling Best Practices

1. **Always catch errors** in store actions
2. **Use error.userMessage** for user-facing error messages
3. **Check error.validationErrors** for field-specific validation errors (400 errors)
4. **Let the interceptor handle 401 errors** - it will automatically redirect to login

## Automatic Token Refresh

The client automatically handles token expiration:
- When a 401 error occurs, the token is cleared from localStorage
- The user is redirected to the login page
- No manual token refresh logic is needed

## Testing

Unit tests are located in `frontend/tests/unit/api-client.test.js`.

To run tests:
```bash
npm run test
```

## Requirements Satisfied

This implementation satisfies the following requirements:
- **6.1**: GET /api/configs endpoint
- **6.2**: GET /api/configs/:session_id endpoint
- **6.3**: PUT /api/configs/:session_id endpoint
- **6.4**: DELETE /api/configs/:session_id endpoint
- **6.5**: GET /api/configs/:session_id/effective endpoint
