<template>
  <div class="sessions-container">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">会话记录</h1>
      <p class="page-subtitle">查看和管理所有会话的历史记录</p>
    </div>

    <!-- Filters -->
    <div class="filters">
      <el-input
        v-model="searchQuery"
        placeholder="搜索用户ID、会话ID、群ID或群名称..."
        clearable
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-button @click="loadSessions" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
      <p>加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <el-icon :size="40" color="#f56c6c">
        <CircleClose />
      </el-icon>
      <p class="error-message">{{ error }}</p>
      <el-button type="primary" @click="loadSessions">
        <el-icon><Refresh /></el-icon>
        重试
      </el-button>
    </div>

    <!-- Sessions Table -->
    <div v-else-if="filteredSessions.length > 0" class="sessions-table">
      <el-table
        :data="paginatedSessions"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
        :row-style="{ cursor: 'pointer' }"
      >
        <el-table-column prop="session_id" label="Session ID" width="280">
          <template #default="{ row }">
            <el-text truncated>{{ row.session_id }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="user_id" label="User ID" width="150" />
        
        <el-table-column prop="chat_id" label="Chat ID" width="200">
          <template #default="{ row }">
            <el-text truncated>{{ row.chat_id || '-' }}</el-text>
          </template>
        </el-table-column>

        <el-table-column prop="chat_name" label="飞书群名称" width="220">
          <template #default="{ row }">
            <el-text truncated>{{ row.chat_name || '-' }}</el-text>
          </template>
        </el-table-column>

        <el-table-column label="消息数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.message_count }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTimestamp(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="最后活跃" width="180">
          <template #default="{ row }">
            {{ formatTimestamp(row.last_active) }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '活跃' : '已归档' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click.stop="viewSession(row)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredSessions.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-container">
      <el-empty description="暂无会话记录" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Loading, 
  CircleClose, 
  Refresh,
  Search
} from '@element-plus/icons-vue'
import { sessionAPI } from '@/api/client'

const router = useRouter()

const sessions = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// Filtered sessions based on search query
const filteredSessions = computed(() => {
  if (!searchQuery.value) return sessions.value
  
  const query = searchQuery.value.toLowerCase()
  return sessions.value.filter(session => 
    session.session_id.toLowerCase().includes(query) ||
    session.user_id.toLowerCase().includes(query) ||
    (session.chat_id && session.chat_id.toLowerCase().includes(query)) ||
    (session.chat_name && session.chat_name.toLowerCase().includes(query))
  )
})

// Paginated sessions
const paginatedSessions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSessions.value.slice(start, end)
})

// Load sessions
const loadSessions = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await sessionAPI.getSessions()
    sessions.value = response.data.data.sessions || []
    ElMessage.success('会话记录加载成功')
  } catch (err) {
    error.value = err.userMessage || '加载会话记录失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// Format timestamp
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Handle row click
const handleRowClick = (row) => {
  viewSession(row)
}

// View session detail
const viewSession = (session) => {
  router.push(`/sessions/${session.session_id}`)
}

// Handle page size change
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
}

// Handle current page change
const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}

// Load sessions on mount
onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.sessions-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* Filters */
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #909399;
}

.loading-container p {
  margin-top: 16px;
  font-size: 14px;
}

/* Error State */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.error-message {
  margin: 16px 0;
  font-size: 14px;
  color: #f56c6c;
}

/* Sessions Table */
.sessions-table {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* Pagination */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Empty State */
.empty-container {
  padding: 80px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .sessions-container {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .filters {
    flex-direction: column;
  }

  .search-input {
    max-width: 100%;
  }

  .sessions-table {
    padding: 12px;
  }
}
</style>
