<template>
  <div class="config-list-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">会话配置管理</h1>
        <p class="page-subtitle">查看和管理所有会话的配置信息</p>
      </div>
      <div class="header-actions">
        <el-button 
          :icon="Refresh" 
          @click="handleRefresh"
          :loading="loading"
        >
          刷新
        </el-button>
        <el-button 
          type="primary" 
          :icon="Download"
          @click="handleExport"
          :loading="exporting"
        >
          导出配置
        </el-button>
        <el-button 
          type="success" 
          :icon="Upload"
          @click="handleImportClick"
        >
          导入配置
        </el-button>
        <input 
          ref="fileInput" 
          type="file" 
          accept=".json"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
    </div>

    <!-- Filters and Search -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-container">
        <div class="filter-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索 Session ID..."
            :prefix-icon="Search"
            clearable
            class="search-input"
            @input="handleSearch"
          />
          <el-select
            v-model="filterType"
            placeholder="筛选类型"
            clearable
            class="filter-select"
            @change="handleFilter"
          >
            <el-option label="全部类型" value="" />
            <el-option label="用户会话" value="user" />
            <el-option label="群组会话" value="group" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-radio-group v-model="sortOrder" @change="handleSort">
            <el-radio-button label="desc">最新优先</el-radio-button>
            <el-radio-button label="asc">最早优先</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </el-card>

    <!-- Config Table -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="displayedConfigs"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
        :row-class-name="getRowClassName"
        empty-text="暂无配置数据"
        class="config-table"
      >
        <el-table-column 
          prop="session_id" 
          label="Session ID" 
          min-width="200"
          show-overflow-tooltip
          class-name="mobile-primary-column"
        >
          <template #default="{ row }">
            <div class="session-id-cell">
              <el-icon class="cell-icon"><User /></el-icon>
              <span class="session-id-text">{{ row.session_id }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column 
          prop="session_type" 
          label="会话类型" 
          width="120"
          align="center"
          class-name="mobile-hide-column"
        >
          <template #default="{ row }">
            <el-tag 
              :type="row.session_type === 'user' ? 'primary' : 'success'"
              effect="light"
              round
            >
              {{ row.session_type === 'user' ? '用户' : '群组' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column 
          label="更新时间" 
          width="200"
          align="center"
          class-name="mobile-secondary-column"
        >
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon class="cell-icon"><Clock /></el-icon>
              <span>{{ formatTime(row.metadata?.updated_at || row.metadata?.created_at) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column 
          label="配置信息" 
          min-width="250"
          class-name="mobile-hide-column"
        >
          <template #default="{ row }">
            <div class="config-preview">
              <el-tag 
                v-if="row.config?.default_provider" 
                size="small" 
                class="config-tag"
              >
                {{ row.config.default_provider }}
              </el-tag>
              <el-tag 
                v-if="row.config?.default_layer" 
                size="small" 
                type="info"
                class="config-tag"
              >
                {{ row.config.default_layer }}
              </el-tag>
              <el-tag 
                v-if="row.config?.response_language" 
                size="small" 
                type="warning"
                class="config-tag"
              >
                {{ row.config.response_language }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column 
          label="操作" 
          width="100"
          align="center"
          fixed="right"
          class-name="mobile-action-column"
        >
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link
              :icon="View"
              @click.stop="handleViewDetail(row.session_id)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Empty State -->
      <div v-if="!loading && displayedConfigs.length === 0" class="empty-state">
        <el-empty description="暂无配置数据">
          <template #image>
            <el-icon :size="80" color="#d1d5db">
              <Document />
            </el-icon>
          </template>
          <el-button type="primary" @click="handleRefresh">刷新数据</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import toast from '@/utils/toast'
import { 
  Refresh, 
  Download, 
  Upload, 
  Search, 
  User, 
  Clock, 
  View,
  Document
} from '@element-plus/icons-vue'

const router = useRouter()
const configStore = useConfigStore()

// Reactive state
const searchQuery = ref('')
const filterType = ref('')
const sortOrder = ref('desc')
const loading = ref(false)
const exporting = ref(false)
const fileInput = ref(null)

// Computed properties
const displayedConfigs = computed(() => {
  let configs = [...configStore.configs]

  // Apply search filter
  if (searchQuery.value) {
    const term = searchQuery.value.toLowerCase()
    configs = configs.filter(config => 
      config.session_id.toLowerCase().includes(term)
    )
  }

  // Apply type filter
  if (filterType.value) {
    configs = configs.filter(config => 
      config.session_type === filterType.value
    )
  }

  // Apply sorting
  configs.sort((a, b) => {
    const timeA = new Date(a.metadata?.updated_at || a.metadata?.created_at)
    const timeB = new Date(b.metadata?.updated_at || b.metadata?.created_at)
    return sortOrder.value === 'desc' ? timeB - timeA : timeA - timeB
  })

  return configs
})

// Methods
const loadConfigs = async () => {
  loading.value = true
  try {
    await configStore.fetchConfigs()
  } catch (error) {
    toast.apiError(error, '加载配置列表失败')
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadConfigs()
  toast.success('刷新成功')
}

const handleSearch = () => {
  // Search is reactive through computed property
}

const handleFilter = () => {
  // Filter is reactive through computed property
}

const handleSort = () => {
  // Sort is reactive through computed property
}

const handleRowClick = (row) => {
  router.push(`/configs/${row.session_id}`)
}

const handleViewDetail = (sessionId) => {
  router.push(`/configs/${sessionId}`)
}

const getRowClassName = () => {
  return 'clickable-row'
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // Less than 1 minute
  if (diff < 60000) {
    return '刚刚'
  }
  
  // Less than 1 hour
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes} 分钟前`
  }
  
  // Less than 1 day
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours} 小时前`
  }
  
  // Less than 7 days
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days} 天前`
  }
  
  // Format as date
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleExport = async () => {
  exporting.value = true
  try {
    await configStore.exportConfigs()
    toast.success('配置导出成功')
  } catch (error) {
    toast.apiError(error, '导出配置失败')
  } finally {
    exporting.value = false
  }
}

const handleImportClick = () => {
  fileInput.value.click()
}

const handleImportFile = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const result = await configStore.importConfigs(file)
    toast.success(`成功导入 ${result.imported_count} 个配置`)
    // Clear file input
    event.target.value = ''
  } catch (error) {
    toast.apiError(error, '导入配置失败')
    event.target.value = ''
  }
}

// Lifecycle
onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.config-list-page {
  padding: 24px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  animation: slideDown 0.4s ease-out;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Filter Card */
.filter-card {
  margin-bottom: 16px;
  border-radius: 12px;
  animation: fadeIn 0.4s ease-out 0.1s both;
}

.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.filter-left {
  display: flex;
  gap: 12px;
  flex: 1;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 150px;
}

.filter-right {
  display: flex;
  align-items: center;
}

/* Table Card */
.table-card {
  border-radius: 12px;
  animation: fadeIn 0.4s ease-out 0.2s both;
}

/* Table Styles */
:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table__header th) {
  background-color: var(--el-fill-color-light);
  font-weight: 600;
  color: var(--el-text-color-primary);
  padding: 16px 0;
}

:deep(.el-table__body td) {
  padding: 14px 0;
}

:deep(.clickable-row) {
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.clickable-row:hover) {
  background-color: var(--el-color-primary-light-9) !important;
  transform: translateY(-1px);
}

/* Mobile table column visibility */
@media (max-width: 768px) {
  :deep(.mobile-hide-column) {
    display: none !important;
  }

  :deep(.mobile-action-column) {
    width: 80px !important;
  }
}

/* Cell Styles */
.session-id-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cell-icon {
  color: var(--el-color-primary);
  font-size: 16px;
}

.session-id-text {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 13px;
  color: var(--el-text-color-primary);
}

.time-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.config-preview {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.config-tag {
  font-size: 12px;
  font-weight: 500;
}

/* Empty State */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* Animations */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .config-list-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 120px;
  }

  .filter-container {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left {
    flex-direction: column;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }

  .filter-right {
    justify-content: center;
  }

  .filter-right .el-radio-group {
    width: 100%;
  }

  .filter-right .el-radio-button {
    flex: 1;
  }

  /* Hide some table columns on mobile */
  :deep(.el-table__column) {
    font-size: 12px;
  }

  /* Make session ID column narrower */
  .session-id-text {
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 150px;
  }

  /* Stack config tags vertically */
  .config-preview {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 13px;
  }
}

/* Extra small screens */
@media (max-width: 480px) {
  .config-list-page {
    padding: 12px;
  }

  .page-title {
    font-size: 20px;
  }

  .header-actions .el-button {
    font-size: 13px;
    padding: 8px 12px;
  }

  .filter-card {
    margin-bottom: 12px;
  }

  .session-id-text {
    max-width: 100px;
  }
}

/* Hover Effects */
.el-button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.el-button:hover {
  transform: translateY(-1px);
}

.el-button:active {
  transform: translateY(0);
}

/* Tag Animations */
.el-tag {
  animation: tagFadeIn 0.3s ease-out;
}

@keyframes tagFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
