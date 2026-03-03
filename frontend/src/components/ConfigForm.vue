<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-width="160px"
    label-position="left"
    @submit.prevent="handleSubmit"
    class="config-form"
  >
    <!-- Target Project Directory -->
    <el-form-item label="项目目录" prop="target_project_dir">
      <el-input
        v-model="formData.target_project_dir"
        placeholder="请输入项目目录路径"
        clearable
      >
        <template #prepend>
          <el-icon><Folder /></el-icon>
        </template>
      </el-input>
      <template #extra>
        <span class="form-hint">留空则使用全局默认值</span>
      </template>
      <!-- Directory warning -->
      <el-alert
        v-if="directoryWarning"
        :title="directoryWarning"
        type="warning"
        :closable="false"
        show-icon
        style="margin-top: 8px"
      />
    </el-form-item>

    <!-- Response Language -->
    <el-form-item label="响应语言" prop="response_language">
      <el-input
        v-model="formData.response_language"
        placeholder="例如：中文、English"
        clearable
      >
        <template #prepend>
          <el-icon><ChatDotRound /></el-icon>
        </template>
      </el-input>
      <template #extra>
        <span class="form-hint">留空则使用全局默认值</span>
      </template>
    </el-form-item>

    <!-- Default Provider -->
    <el-form-item label="默认提供商" prop="default_provider">
      <el-select
        v-model="formData.default_provider"
        placeholder="请选择提供商"
        clearable
        style="width: 100%"
      >
        <el-option label="Claude" value="claude" />
        <el-option label="Gemini" value="gemini" />
        <el-option label="OpenAI" value="openai" />
      </el-select>
      <template #extra>
        <span class="form-hint">留空则使用全局默认值</span>
      </template>
    </el-form-item>

    <!-- Default Layer -->
    <el-form-item label="默认层级" prop="default_layer">
      <el-select
        v-model="formData.default_layer"
        placeholder="请选择层级"
        clearable
        style="width: 100%"
      >
        <el-option label="API" value="api" />
        <el-option label="CLI" value="cli" />
      </el-select>
      <template #extra>
        <span class="form-hint">留空则使用全局默认值</span>
      </template>
    </el-form-item>

    <!-- Default CLI Provider -->
    <el-form-item label="默认 CLI 提供商" prop="default_cli_provider">
      <el-select
        v-model="formData.default_cli_provider"
        placeholder="请选择 CLI 提供商"
        clearable
        style="width: 100%"
      >
        <el-option label="Claude" value="claude" />
        <el-option label="Gemini" value="gemini" />
        <el-option label="OpenAI" value="openai" />
      </el-select>
      <template #extra>
        <span class="form-hint">留空则使用全局默认值</span>
      </template>
    </el-form-item>

    <!-- Form Actions -->
    <el-form-item>
      <el-button 
        type="primary" 
        @click="handleSubmit" 
        :loading="saving" 
        :disabled="saving"
        :icon="Check"
      >
        {{ saving ? '保存中...' : '保存配置' }}
      </el-button>
      <el-button @click="handleReset" :disabled="saving">
        重置表单
      </el-button>
    </el-form-item>

    <!-- Validation Errors Display -->
    <el-alert
      v-if="validationError"
      type="error"
      :title="validationError"
      show-icon
      closable
      @close="validationError = null"
      style="margin-top: 16px"
    />
  </el-form>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useConfigStore } from '@/stores/config'
import toast from '@/utils/toast'
import { Folder, ChatDotRound, Check } from '@element-plus/icons-vue'

const props = defineProps({
  config: {
    type: Object,
    required: true
  },
  sessionId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['save-success'])

const configStore = useConfigStore()
const formRef = ref(null)
const saving = ref(false)
const validationError = ref(null)
const directoryWarning = ref(null)

// Form data
const formData = reactive({
  target_project_dir: '',
  response_language: '',
  default_provider: '',
  default_layer: '',
  default_cli_provider: ''
})

// Validation rules
const rules = {
  target_project_dir: [
    { max: 500, message: '路径长度不能超过 500 个字符', trigger: 'blur' }
  ],
  response_language: [
    { max: 50, message: '语言名称长度不能超过 50 个字符', trigger: 'blur' }
  ],
  default_provider: [
    {
      validator: (rule, value, callback) => {
        if (value && !['claude', 'gemini', 'openai'].includes(value)) {
          callback(new Error('提供商必须是 claude、gemini 或 openai'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  default_layer: [
    {
      validator: (rule, value, callback) => {
        if (value && !['api', 'cli'].includes(value)) {
          callback(new Error('层级必须是 api 或 cli'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  default_cli_provider: [
    {
      validator: (rule, value, callback) => {
        if (value && !['claude', 'gemini', 'openai'].includes(value)) {
          callback(new Error('CLI 提供商必须是 claude、gemini 或 openai'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// Initialize form data from props
function initFormData() {
  formData.target_project_dir = props.config.target_project_dir || ''
  formData.response_language = props.config.response_language || ''
  formData.default_provider = props.config.default_provider || ''
  formData.default_layer = props.config.default_layer || ''
  formData.default_cli_provider = props.config.default_cli_provider || ''
}

// Watch for config changes
watch(() => props.config, () => {
  initFormData()
}, { immediate: true, deep: true })

// Watch for directory path changes to show warning
watch(() => formData.target_project_dir, (newPath) => {
  if (newPath && newPath.trim()) {
    // Check if path looks like a valid directory path
    // This is a client-side heuristic check
    const isValidFormat = /^[a-zA-Z]:[\\\/]|^\/|^~\/|^\.\.?\//.test(newPath.trim())
    
    if (!isValidFormat) {
      directoryWarning.value = '目录路径格式可能不正确，但仍可保存'
    } else {
      directoryWarning.value = null
    }
  } else {
    directoryWarning.value = null
  }
})

// Handle form submit
async function handleSubmit() {
  if (!formRef.value) return

  try {
    // Validate form
    await formRef.value.validate()

    // Clear previous validation error
    validationError.value = null

    // Prepare data (only send non-empty values)
    const updateData = {}
    if (formData.target_project_dir) {
      updateData.target_project_dir = formData.target_project_dir
    }
    if (formData.response_language) {
      updateData.response_language = formData.response_language
    }
    if (formData.default_provider) {
      updateData.default_provider = formData.default_provider
    }
    if (formData.default_layer) {
      updateData.default_layer = formData.default_layer
    }
    if (formData.default_cli_provider) {
      updateData.default_cli_provider = formData.default_cli_provider
    }

    // If all fields are empty, we need to send at least session_type
    if (Object.keys(updateData).length === 0) {
      toast.warning('请至少填写一个配置项')
      return
    }

    saving.value = true

    // Save config
    await configStore.updateConfig(props.sessionId, updateData)

    toast.success('配置保存成功')
    emit('save-success')
  } catch (error) {
    console.error('Failed to save config:', error)

    // Display validation errors from server
    if (error.validationErrors) {
      validationError.value = error.validationErrors
    } else {
      toast.apiError(error, '保存配置失败')
    }
  } finally {
    saving.value = false
  }
}

// Handle form reset
function handleReset() {
  initFormData()
  formRef.value?.clearValidate()
  validationError.value = null
  directoryWarning.value = null
}
</script>

<style scoped>
.config-form {
  padding: 20px 0;
  max-width: 800px;
}

.form-hint {
  font-size: 12px;
  color: #909399;
}

/* Desktop optimizations */
@media (min-width: 769px) {
  .config-form {
    padding: 24px 0;
  }

  :deep(.el-form-item) {
    margin-bottom: 24px;
  }

  :deep(.el-input),
  :deep(.el-select) {
    max-width: 500px;
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .config-form {
    padding: 16px 0;
  }

  :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left;
    margin-bottom: 8px;
    line-height: 1.5;
  }

  :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-input),
  :deep(.el-select) {
    width: 100% !important;
    max-width: none !important;
  }

  :deep(.el-button) {
    width: 100%;
    margin-bottom: 8px;
  }

  .form-hint {
    font-size: 11px;
  }
}

/* Extra small screens */
@media (max-width: 480px) {
  .config-form {
    padding: 12px 0;
  }

  :deep(.el-form-item__label) {
    font-size: 13px;
  }

  :deep(.el-input__inner) {
    font-size: 14px;
  }
}
</style>
