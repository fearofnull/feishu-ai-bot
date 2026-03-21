<template>
  <div class="tools-container">
    <div class="tools-header">
      <h1>工具管理</h1>
      <p>管理内置工具及其启用状态。禁用的工具将对代理不可用。</p>
      <div class="tools-actions">
        <el-button 
          type="primary" 
          @click="enableAll" 
          :disabled="loading || batchLoading || !hasDisabledTools"
        >
          全部启用
        </el-button>
        <el-button 
          type="danger" 
          @click="disableAll" 
          :disabled="loading || batchLoading || !hasEnabledTools"
        >
          全部禁用
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="tools.length === 0" class="empty-container">
      <el-empty description="暂无工具" />
    </div>

    <div v-else class="tools-list">
      <el-table :data="tools" stripe style="width: 100%">
        <el-table-column prop="name" label="工具名称" min-width="200">
          <template #default="{ row }">
            <span class="tool-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="300">
          <template #default="{ row }">
            <span class="tool-description">{{ row.description }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
              {{ row.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-switch 
              v-model="row.enabled" 
              @change="handleToggle(row)"
              :loading="toggleLoading[row.name]"
            />
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElEmpty, ElSwitch, ElButton, ElIcon, ElTable, ElTableColumn, ElTag } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'

const authStore = useAuthStore()
const tools = ref([])
const loading = ref(false)
const batchLoading = ref(false)
const toggleLoading = ref({})

const hasDisabledTools = computed(() => {
  return tools.value.some(tool => !tool.enabled)
})

const hasEnabledTools = computed(() => {
  return tools.value.some(tool => tool.enabled)
})

const loadTools = async () => {
  loading.value = true
  try {
    const response = await client.get('/tools')
    tools.value = response.data.data
  } catch (error) {
    console.error('加载工具失败:', error)
    ElMessage.error('加载工具失败')
  } finally {
    loading.value = false
  }
}

const handleToggle = async (tool) => {
  toggleLoading.value[tool.name] = true
  try {
    const response = await client.post(`/tools/${tool.name}/toggle`)
    // 更新工具状态
    const updatedTool = response.data.data
    const index = tools.value.findIndex(t => t.name === tool.name)
    if (index !== -1) {
      tools.value[index] = updatedTool
    }
    ElMessage.success(updatedTool.enabled ? '工具已启用' : '工具已禁用')
  } catch (error) {
    console.error('切换工具状态失败:', error)
    // 恢复原始状态
    tool.enabled = !tool.enabled
    ElMessage.error('切换工具状态失败')
  } finally {
    toggleLoading.value[tool.name] = false
  }
}

const enableAll = async () => {
  batchLoading.value = true
  try {
    await client.post('/tools/enable-all')
    // 更新所有工具状态
    tools.value.forEach(tool => {
      tool.enabled = true
    })
    ElMessage.success('所有工具已启用')
  } catch (error) {
    console.error('启用所有工具失败:', error)
    ElMessage.error('启用所有工具失败')
  } finally {
    batchLoading.value = false
  }
}

const disableAll = async () => {
  batchLoading.value = true
  try {
    await client.post('/tools/disable-all')
    // 更新所有工具状态
    tools.value.forEach(tool => {
      tool.enabled = false
    })
    ElMessage.success('所有工具已禁用')
  } catch (error) {
    console.error('禁用所有工具失败:', error)
    ElMessage.error('禁用所有工具失败')
  } finally {
    batchLoading.value = false
  }
}

onMounted(() => {
  loadTools()
})
</script>

<style scoped>
.tools-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.tools-header {
  margin-bottom: 32px;
}

.tools-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.tools-header p {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.tools-actions {
  display: flex;
  gap: 12px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
}

.loading-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-container {
  padding: 64px 0;
}

.tools-list {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.tools-list :deep(.el-table__body tr:hover > td) {
  background-color: #e6f7ff !important;
}

.tool-name {
  font-weight: 600;
  color: #333;
}

.tool-description {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .tools-container {
    padding: 16px;
  }

  .tools-actions {
    flex-direction: column;
  }
}
</style>