<template>
  <div class="session-detail-container">
    <!-- Back Button -->
    <el-button @click="goBack" class="back-button">
      <el-icon><ArrowLeft /></el-icon>
      返回
    </el-button>

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
      <el-button type="primary" @click="loadSession">
        <el-icon><Refresh /></el-icon>
        重试
      </el-button>
    </div>

    <!-- Session Content -->
    <div v-else-if="session" class="session-content">
      <!-- Session Info Card -->
      <el-card shadow="hover" class="info-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><ChatDotRound /></el-icon>
            <span>会话信息</span>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Session ID">
            <el-text>{{ session.session_id }}</el-text>
          </el-descriptions-item>
          
          <el-descriptions-item label="User ID">
            <el-text>{{ session.user_id }}</el-text>
          </el-descriptions-item>
          
          <el-descriptions-item label="Chat ID">
            <el-text>{{ session.chat_id || '-' }}</el-text>
          </el-descriptions-item>
          
          <el-descriptions-item label="创建时间">
            {{ formatTimestamp(session.created_at) }}
          </el-descriptions-item>
          
          <el-descriptions-item label="最后活跃">
            {{ formatTimestamp(session.last_active) }}
          </el-descriptions-item>
          
          <el-descriptions-item label="消息数量">
            <el-tag type="info">{{ session.messages?.length || 0 }} 条</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="状态">
            <el-tag :type="session.status === 'active' ? 'success' : 'info'">
              {{ session.status === 'active' ? '活跃' : '已归档' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Messages Card -->
      <el-card shadow="hover" class="messages-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><ChatLineRound /></el-icon>
            <span>对话记录</span>
          </div>
        </template>

        <div class="messages-container">
          <div
            v-for="(message, index) in session.messages"
            :key="index"
            :class="['message-item', message.role]"
          >
            <div class="message-header">
              <div class="message-role">
                <el-icon v-if="message.role === 'user'" :size="16"><User /></el-icon>
                <el-icon v-else :size="16"><Service /></el-icon>
                <span>{{ message.role === 'user' ? '用户' : 'AI助手' }}</span>
              </div>
              <div class="message-time">
                {{ formatTimestamp(message.timestamp) }}
              </div>
            </div>
            
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-container">
      <el-empty description="未找到会话记录" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Loading, 
  CircleClose, 
  Refresh,
  ArrowLeft,
  ChatDotRound,
  ChatLineRound,
  User,
  Service
} from '@element-plus/icons-vue'
import { sessionAPI } from '@/api/client'

const route = useRoute()
const router = useRouter()

const session = ref(null)
const loading = ref(false)
const error = ref(null)

// Load session detail
const loadSession = async () => {
  loading.value = true
  error.value = null
  
  try {
    const sessionId = route.params.id
    const response = await sessionAPI.getSession(sessionId)
    session.value = response.data.data
  } catch (err) {
    error.value = err.userMessage || '加载会话详情失败'
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

// Format message content (convert markdown-like syntax to HTML)
const formatMessage = (content) => {
  if (!content) return ''
  
  // Escape HTML
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // Convert code blocks
  formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code class="language-${lang || 'text'}">${code.trim()}</code></pre>`
  })
  
  // Convert inline code
  formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  // Convert bold
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  
  // Convert line breaks
  formatted = formatted.replace(/\n/g, '<br>')
  
  return formatted
}

// Go back to sessions list
const goBack = () => {
  router.push('/sessions')
}

// Load session on mount
onMounted(() => {
  loadSession()
})
</script>

<style scoped>
.session-detail-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Back Button */
.back-button {
  margin-bottom: 20px;
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

/* Session Content */
.session-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Info Card */
.info-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* Messages Card */
.messages-card {
  border-radius: 8px;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Message Item */
.message-item {
  padding: 16px;
  border-radius: 8px;
  background: #f5f7fa;
}

.message-item.user {
  background: #e6f7ff;
  border-left: 4px solid #1890ff;
}

.message-item.assistant {
  background: #f0f9ff;
  border-left: 4px solid #52c41a;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.message-role {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #303133;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-content {
  color: #606266;
  line-height: 1.6;
}

.message-text :deep(pre) {
  background: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text :deep(code) {
  background: #f4f4f5;
  color: #e83e8c;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.message-text :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.message-text :deep(strong) {
  font-weight: 600;
  color: #303133;
}

/* Empty State */
.empty-container {
  padding: 80px 20px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .session-detail-container {
    padding: 16px;
  }

  .message-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .message-item {
    padding: 12px;
  }
}
</style>
