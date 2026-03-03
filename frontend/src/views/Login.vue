<template>
  <div class="login-container">
    <div class="login-card-wrapper">
      <el-card class="login-card" shadow="always">
        <template #header>
          <div class="card-header">
            <div class="logo-wrapper">
              <div class="logo-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            <h1 class="title">飞书 AI Bot</h1>
            <p class="subtitle">管理控制台</p>
          </div>
        </template>
        
        <el-form 
          ref="loginFormRef"
          :model="loginForm" 
          :rules="rules"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入管理员密码"
              size="large"
              show-password
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
              :disabled="loading"
              clearable
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-alert
            v-if="errorMessage"
            :title="errorMessage"
            type="error"
            :closable="false"
            show-icon
            class="error-alert"
          />
          
          <el-form-item class="login-button-wrapper">
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              :disabled="!loginForm.password"
              @click="handleLogin"
              class="login-button"
            >
              <span v-if="!loading">登录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="footer-info">
          <el-icon class="info-icon"><InfoFilled /></el-icon>
          <span>请使用环境变量 WEB_ADMIN_PASSWORD 配置的密码登录</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import toast from '@/utils/toast'
import { Lock, InfoFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const loginForm = reactive({
  password: ''
})

const rules = {
  password: [
    { required: true, message: '请输入管理员密码', trigger: 'blur' },
    { min: 1, message: '密码不能为空', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  // Clear previous error
  errorMessage.value = ''
  
  // Validate form
  if (!loginFormRef.value) {
    return
  }
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) {
      return
    }
  } catch (error) {
    return
  }
  
  // Start loading
  loading.value = true
  
  try {
    // Call login API through auth store
    await authStore.login(loginForm.password)
    
    // Show success message
    toast.success('登录成功！')
    
    // Redirect to config list
    setTimeout(() => {
      router.push('/configs')
    }, 500)
    
  } catch (error) {
    // Handle login error
    console.error('Login failed:', error)
    
    // Extract error message
    let message = '登录失败，请检查密码是否正确'
    
    if (error.response) {
      // Server responded with error
      if (error.response.status === 401) {
        message = '密码错误，请重试'
      } else if (error.response.data?.message) {
        message = error.response.data.message
      } else if (error.response.data?.error) {
        message = error.response.data.error
      }
    } else if (error.request) {
      // Request made but no response
      message = '无法连接到服务器，请检查网络连接'
    }
    
    // Display error message
    errorMessage.value = message
    
    // Also show toast notification
    toast.error(message)
    
  } finally {
    // Stop loading
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: backgroundMove 20s linear infinite;
}

@keyframes backgroundMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.login-card-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-card {
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.98);
}

.login-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 2.5rem 2rem 2rem;
}

.login-card :deep(.el-card__body) {
  padding: 2rem;
}

.card-header {
  text-align: center;
  color: white;
}

.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.logo-icon svg {
  width: 36px;
  height: 36px;
  color: white;
}

.title {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: white;
  letter-spacing: 0.5px;
}

.subtitle {
  margin: 0;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

.login-form {
  margin-top: 0.5rem;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 1.5rem;
}

.login-form :deep(.el-input__wrapper) {
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
}

.error-alert {
  margin-bottom: 1.5rem;
  border-radius: 8px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.login-button-wrapper {
  margin-bottom: 0;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.footer-info {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.info-icon {
  color: #667eea;
  font-size: 1rem;
}

/* Responsive design */
@media (max-width: 640px) {
  .login-container {
    padding: 1rem;
  }
  
  .login-card :deep(.el-card__header) {
    padding: 2rem 1.5rem 1.5rem;
  }
  
  .login-card :deep(.el-card__body) {
    padding: 1.5rem;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .subtitle {
    font-size: 0.875rem;
  }
  
  .logo-icon {
    width: 56px;
    height: 56px;
  }
  
  .logo-icon svg {
    width: 32px;
    height: 32px;
  }
  
  .footer-info {
    font-size: 0.8rem;
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>
