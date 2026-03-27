<template>
  <div class="config-detail-container">
    <!-- Header with back button -->
    <div class="header">
      <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
      <h1>配置详情</h1>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Error state -->
    <el-alert
      v-else-if="error"
      type="error"
      :title="error"
      show-icon
      :closable="false"
    />

    <!-- Config content -->
    <div v-else-if="currentConfig" class="config-content">
      <!-- Session Info Card -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>会话信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Session ID">
            {{ currentConfig.session_id }}
          </el-descriptions-item>
          <el-descriptions-item label="会话类型">
            <el-tag :type="currentConfig.session_type === 'user' ? 'success' : 'primary'">
              {{ currentConfig.session_type === 'user' ? '用户' : '群组' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentConfig.chat_name" label="飞书群名称">
            {{ currentConfig.chat_name }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Config/Effective Config Toggle -->
      <div class="view-toggle">
        <el-radio-group v-model="viewMode" size="large">
          <el-radio-button label="config">配置</el-radio-button>
          <el-radio-button label="effective">有效配置</el-radio-button>
        </el-radio-group>
      </div>

      <!-- Config Form (Edit Mode) -->
      <el-card v-if="viewMode === 'config'" class="config-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>配置设置</span>
            <div class="card-actions">
              <el-button type="danger" @click="handleReset" :icon="Delete">
                重置配置
              </el-button>
            </div>
          </div>
        </template>
        <ConfigForm
          :config="currentConfig.config"
          :session-id="currentConfig.session_id"
          @save-success="handleSaveSuccess"
        />
      </el-card>

      <!-- Effective Config (Read-only) -->
      <el-card v-else class="config-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>有效配置（应用优先级规则后）</span>
            <el-button
              type="primary"
              @click="loadEffectiveConfig"
              :icon="Refresh"
              :loading="loadingEffective"
            >
              刷新
            </el-button>
          </div>
        </template>
        <div v-if="loadingEffective" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        <el-descriptions v-else-if="effectiveConfig" :column="1" border>
          <el-descriptions-item label="项目目录">
            <span :class="{ 'default-value': !currentConfig.config.target_project_dir }">
              {{ effectiveConfig.target_project_dir || '(未设置)' }}
            </span>
            <el-tag v-if="!currentConfig.config.target_project_dir" size="small" type="info" class="value-tag">
              默认值
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="响应语言">
            <span :class="{ 'default-value': !currentConfig.config.response_language }">
              {{ effectiveConfig.response_language || '(未设置)' }}
            </span>
            <el-tag v-if="!currentConfig.config.response_language" size="small" type="info" class="value-tag">
              默认值
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="默认 CLI 提供商">
            <span :class="{ 'default-value': !currentConfig.config.default_cli_provider }">
              {{ effectiveConfig.default_cli_provider || '(未设置)' }}
            </span>
            <el-tag v-if="!currentConfig.config.default_cli_provider" size="small" type="info" class="value-tag">
              默认值
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Metadata Card -->
      <el-card class="metadata-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>元数据</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="创建者">
            {{ currentConfig.metadata?.created_by || '(未知)' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentConfig.metadata?.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新者">
            {{ currentConfig.metadata?.updated_by || '(未知)' }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(currentConfig.metadata?.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新次数" :span="2">
            {{ currentConfig.metadata?.update_count || 0 }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- Not found state -->
    <el-empty v-else description="配置不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import { ElMessageBox } from 'element-plus'
import toast from '@/utils/toast'
import { ArrowLeft, Delete, Refresh } from '@element-plus/icons-vue'
import ConfigForm from '@/components/ConfigForm.vue'

const route = useRoute()
const router = useRouter()
const configStore = useConfigStore()

const viewMode = ref('config')
const effectiveConfig = ref(null)
const loadingEffective = ref(false)

const sessionId = computed(() => route.params.id)
const currentConfig = computed(() => configStore.currentConfig)
const loading = computed(() => configStore.loading)
const error = computed(() => configStore.error)

// Load config on mount
onMounted(async () => {
  await loadConfig()
})

// Load config data
async function loadConfig() {
  try {
    await configStore.fetchConfig(sessionId.value)
  } catch (err) {
    console.error('Failed to load config:', err)
  }
}

// Load effective config
async function loadEffectiveConfig() {
  loadingEffective.value = true
  try {
    effectiveConfig.value = await configStore.fetchEffectiveConfig(sessionId.value)
  } catch (err) {
    toast.apiError(err, '加载有效配置失败')
    console.error('Failed to load effective config:', err)
  } finally {
    loadingEffective.value = false
  }
}

// Watch view mode changes to load effective config
import { watch } from 'vue'
watch(viewMode, (newMode) => {
  if (newMode === 'effective' && !effectiveConfig.value) {
    loadEffectiveConfig()
  }
})

// Handle save success
function handleSaveSuccess() {
  toast.success('配置保存成功')
  loadConfig()
  // Clear effective config to force reload
  effectiveConfig.value = null
}

// Handle reset config
async function handleReset() {
  try {
    await ElMessageBox.confirm(
      '确定要重置此配置吗？这将删除所有自定义设置并恢复默认值。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await configStore.deleteConfig(sessionId.value)
    toast.success('配置已重置')
    router.push('/configs')
  } catch (err) {
    if (err !== 'cancel') {
      toast.apiError(err, '重置配置失败')
      console.error('Failed to reset config:', err)
    }
  }
}

// Go back to list
function goBack() {
  router.push('/configs')
}

// Format date
function formatDate(dateString) {
  if (!dateString) return '(未知)'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.config-detail-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.loading-container {
  padding: 20px;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card,
.config-card,
.metadata-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.view-toggle {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.default-value {
  color: #909399;
  font-style: italic;
}

.value-tag {
  margin-left: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
  .config-detail-container {
    padding: 12px;
  }

  .header {
    margin-bottom: 16px;
  }

  .header h1 {
    font-size: 20px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .card-actions {
    width: 100%;
  }

  .card-actions .el-button {
    flex: 1;
  }

  .view-toggle {
    margin: 16px 0;
  }

  .view-toggle .el-radio-group {
    width: 100%;
  }

  .view-toggle .el-radio-button {
    flex: 1;
  }

  /* Make descriptions stack vertically */
  :deep(.el-descriptions) {
    font-size: 13px;
  }

  :deep(.el-descriptions__label) {
    width: 100% !important;
    text-align: left !important;
  }

  :deep(.el-descriptions__content) {
    width: 100% !important;
    display: block !important;
    padding-left: 0 !important;
  }

  .config-content {
    gap: 16px;
  }
}

/* Extra small screens */
@media (max-width: 480px) {
  .config-detail-container {
    padding: 8px;
  }

  .header h1 {
    font-size: 18px;
  }

  .header .el-button {
    font-size: 13px;
    padding: 8px 12px;
  }
}
</style>
