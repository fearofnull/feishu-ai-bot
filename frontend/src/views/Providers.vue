<template>
  <div class="providers-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">AI 提供商配置</h1>
        <p class="page-subtitle">管理 AI API 提供商的连接配置</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="loadProviders" :loading="loading">刷新</el-button>
      </div>
    </div>

    <!-- Active Service Config Section -->
    <el-card class="active-config-card" shadow="never">
      <div class="active-config-title">
        <span class="section-label">当前服务配置</span>
        <span class="section-desc">选择提供商和模型，服务将使用此配置响应请求</span>
      </div>
      <div class="active-config-inline">
        <div class="inline-item">
          <span class="inline-label">提供商</span>
          <el-select
            v-model="activeProviderName"
            placeholder="选择提供商"
            style="width: 220px"
            @change="onProviderSelectChange"
          >
            <el-option
              v-for="p in providers"
              :key="p.name"
              :label="p.name"
              :value="p.name"
            >
              <span>{{ p.name }}</span>
              <el-tag :type="typeTagColor(p.type)" size="small" effect="plain" style="margin-left: 8px">{{ typeLabel(p.type) }}</el-tag>
            </el-option>
          </el-select>
        </div>

        <div class="inline-item" v-if="activeProvider">
          <span class="inline-label">模型</span>
          <el-select
            v-model="activeModel"
            placeholder="选择模型"
            style="min-width: 280px; max-width: 480px"
          >
            <el-option
              v-for="m in activeProvider.models"
              :key="m"
              :label="m"
              :value="m"
            />
          </el-select>
        </div>

        <div class="inline-item inline-actions">
          <el-button
            type="primary"
            :disabled="!activeProvider || !activeModel || !hasConfigChanged"
            :loading="savingConfig"
            @click="saveActiveConfig"
          >
            保存配置
          </el-button>
          <span v-if="savedConfig" class="saved-hint">
            当前生效：{{ savedConfig.provider }} / {{ savedConfig.model }}
          </span>
        </div>
      </div>
    </el-card>

    <!-- Provider List -->
    <div class="provider-list-section">
      <div class="section-header">
        <h2 class="section-title">所有提供商</h2>
        <div style="display: flex; align-items: center; gap: 12px;">
          <span class="provider-count">{{ providers.length }} 个</span>
          <el-button type="primary" :icon="Plus" @click="showAddDialog">添加提供商</el-button>
        </div>
      </div>
      <div v-loading="loading" class="provider-grid">
        <el-card
          v-for="provider in providers"
          :key="provider.name"
          class="provider-card"
          shadow="hover"
        >
          <div class="card-content">
            <div class="card-header">
              <div class="card-title-row">
                <span class="provider-name">{{ provider.name }}</span>
                <el-tag :type="typeTagColor(provider.type)" size="small">{{ typeLabel(provider.type) }}</el-tag>
              </div>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="info-label">模型数量</span>
                <span class="info-value">{{ provider.models?.length || 0 }} 个</span>
              </div>
              <div class="info-row">
                <span class="info-label">Base URL</span>
                <span class="info-value mono">{{ provider.base_url || '-' }}</span>
              </div>
            </div>
            <div class="card-actions" @click.stop>
              <el-button type="primary" text :icon="Edit" @click="showEditDialog(provider)">编辑</el-button>
              <el-button type="info" text @click="handleTestProvider(provider)">测试</el-button>
              <el-button type="danger" text :icon="Delete" @click="handleDelete(provider.name)">删除</el-button>
            </div>
          </div>
        </el-card>

        <!-- Empty State -->
        <el-empty v-if="!loading && providers.length === 0" description="暂无提供商配置" class="empty-state">
          <el-button type="primary" @click="showAddDialog">添加第一个提供商</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑提供商' : '添加提供商'"
      width="520px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="如: openai-gpt4" :disabled="isEditing" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="选择提供商类型" style="width: 100%">
            <el-option label="OpenAI 兼容" value="openai_compatible" />
            <el-option label="Claude 兼容" value="claude_compatible" />
            <el-option label="Gemini 兼容" value="gemini_compatible" />
          </el-select>
        </el-form-item>
        <el-form-item label="Base URL" prop="base_url">
          <el-input v-model="form.base_url" placeholder="如: https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="form.api_key" type="password" show-password :placeholder="isEditing ? '留空则保留原有 API Key' : '输入 API Key'" />
        </el-form-item>
        <el-form-item label="模型列表" prop="models">
          <div class="models-input-container">
            <div class="models-list-input">
              <el-tag
                v-for="(model, index) in form.models"
                :key="index"
                closable
                @close="removeModel(index)"
                class="model-tag-input"
              >
                {{ model }}
              </el-tag>
              <el-input
                v-model="newModel"
                placeholder="输入模型名称后按回车添加"
                @keyup.enter="addModel"
                class="model-input"
                size="small"
              />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditing ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Test Provider Dialog -->
    <el-dialog
      v-model="testDialogVisible"
      :title="`测试提供商 ${testingProvider?.name}`"
      width="460px"
      destroy-on-close
    >
      <div style="padding: 4px 0">
        <p style="margin: 0 0 12px; color: var(--el-text-color-secondary); font-size: 13px;">选择要测试的模型：</p>
        <el-select v-model="testSelectedModel" style="width: 100%">
          <el-option
            v-for="m in testingProvider?.models"
            :key="m"
            :label="m"
            :value="m"
          />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="testing" @click="doTestProvider">开始测试</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { providerAPI } from '@/api/client'
import toast from '@/utils/toast'
import { ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'

const providers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingName = ref('')
const submitting = ref(false)
const formRef = ref(null)

// Active service config
const activeProviderName = ref('')
const activeProvider = computed(() => providers.value.find(p => p.name === activeProviderName.value) || null)
const activeModel = ref('')
const savedConfig = ref(null)
const savingConfig = ref(false)

// Test dialog state
const testDialogVisible = ref(false)
const testingProvider = ref(null)
const testSelectedModel = ref('')
const testing = ref(false)

const form = ref({ name: '', type: '', base_url: '', api_key: '', models: [] })
const newModel = ref('')

const API_KEY_PLACEHOLDER = '••••••••••••••••'

const hasConfigChanged = computed(() => {
  if (!savedConfig.value) return true
  return savedConfig.value.provider !== activeProviderName.value ||
         savedConfig.value.model !== activeModel.value
})

const rules = computed(() => ({
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  api_key: isEditing.value ? [] : [{ required: true, message: '请输入 API Key', trigger: 'blur' }],
  models: [
    { required: true, message: '请至少添加一个模型', trigger: 'change' },
    { type: 'array', min: 1, message: '请至少添加一个模型', trigger: 'change' }
  ]
}))

const typeLabel = (type) => {
  const map = { openai_compatible: 'OpenAI', claude_compatible: 'Claude', gemini_compatible: 'Gemini' }
  return map[type] || type
}

const typeTagColor = (type) => {
  const map = { openai_compatible: 'success', claude_compatible: 'warning', gemini_compatible: 'primary' }
  return map[type] || 'info'
}

const loadProviders = async () => {
  loading.value = true
  try {
    const res = await providerAPI.getProviders()
    providers.value = res.data.data || []

    // Init active config from the default provider (only on first load)
    if (providers.value.length > 0 && !activeProviderName.value) {
      const defaultProvider = providers.value.find(p => p.is_default) || providers.value[0]
      activeProviderName.value = defaultProvider.name
      activeModel.value = defaultProvider.default_model || defaultProvider.models?.[0] || ''
      savedConfig.value = { provider: defaultProvider.name, model: activeModel.value }
    }
  } catch (e) {
    toast.apiError(e, '加载提供商列表失败')
  } finally {
    loading.value = false
  }
}

const onProviderSelectChange = (name) => {
  const p = providers.value.find(x => x.name === name)
  if (p) {
    activeModel.value = p.default_model || p.models?.[0] || ''
  }
}

const saveActiveConfig = async () => {
  if (!activeProvider.value || !activeModel.value) return
  savingConfig.value = true
  try {
    await providerAPI.setDefault(activeProvider.value.name)
    const payload = {
      ...activeProvider.value,
      api_key: '',
      default_model: activeModel.value
    }
    await providerAPI.updateProvider(activeProvider.value.name, payload)
    savedConfig.value = { provider: activeProvider.value.name, model: activeModel.value }
    toast.success(`已保存：${activeProvider.value.name} / ${activeModel.value}`)
    loadProviders()
  } catch (e) {
    toast.apiError(e, '保存失败')
  } finally {
    savingConfig.value = false
  }
}

const showAddDialog = () => {
  isEditing.value = false
  editingName.value = ''
  form.value = { name: '', type: '', base_url: '', api_key: '', models: [] }
  newModel.value = ''
  dialogVisible.value = true
}

const showEditDialog = (provider) => {
  isEditing.value = true
  editingName.value = provider.name
  form.value = {
    name: provider.name,
    type: provider.type,
    base_url: provider.base_url || '',
    api_key: API_KEY_PLACEHOLDER,
    models: [...(provider.models || [])]
  }
  newModel.value = ''
  dialogVisible.value = true
}

const addModel = () => {
  const model = newModel.value.trim()
  if (model && !form.value.models.includes(model)) {
    form.value.models.push(model)
    newModel.value = ''
  }
}

const removeModel = (index) => {
  form.value.models.splice(index, 1)
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { ...form.value }
    if (payload.api_key === API_KEY_PLACEHOLDER) payload.api_key = ''
    if (!payload.default_model) payload.default_model = payload.models[0] || ''

    if (isEditing.value) {
      await providerAPI.updateProvider(editingName.value, payload)
      toast.success('提供商配置已更新')
    } else {
      await providerAPI.createProvider(payload)
      toast.success('提供商配置已添加')
    }
    dialogVisible.value = false
    loadProviders()
  } catch (e) {
    toast.apiError(e, isEditing.value ? '更新失败' : '添加失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (name) => {
  try {
    await ElMessageBox.confirm(`确定要删除提供商 "${name}" 吗？`, '确认删除', { type: 'warning' })
    await providerAPI.deleteProvider(name)
    toast.success('提供商已删除')
    if (activeProviderName.value === name) {
      activeProviderName.value = ''
      activeModel.value = ''
      savedConfig.value = null
    }
    loadProviders()
  } catch (e) {
    if (e !== 'cancel') toast.apiError(e, '删除失败')
  }
}

const handleTestProvider = (provider) => {
  const models = provider.models || []
  if (models.length === 0) {
    toast.error('该提供商没有配置模型')
    return
  }
  testingProvider.value = provider
  testSelectedModel.value = models[0]
  testDialogVisible.value = true
}

const doTestProvider = async () => {
  if (!testingProvider.value || !testSelectedModel.value) return
  testing.value = true
  try {
    toast.info(`正在测试 ${testingProvider.value.name} / ${testSelectedModel.value}...`)
    const res = await providerAPI.testProvider(testingProvider.value.name, testSelectedModel.value)
    if (res.data.success) {
      toast.success(res.data.message)
      testDialogVisible.value = false
    } else {
      toast.error(res.data.error?.message || '测试失败')
    }
  } catch (e) {
    toast.error(e.response?.data?.error?.message || e.userMessage || '测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => loadProviders())
</script>

<style scoped>
.providers-page {
  padding: 24px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 8px 0;
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

/* Active Config Section */
.active-config-card {
  margin-bottom: 32px;
  border: 2px solid var(--el-color-primary);
  border-radius: 12px;
}

.active-config-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.section-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.section-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.active-config-inline {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.inline-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.inline-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

.inline-actions {
  gap: 12px;
}

.saved-hint {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* Provider List Section */
.provider-list-section {
  margin-top: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
}

.provider-count {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.provider-card {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.provider-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-content {
  padding: 4px;
}

.card-header {
  margin-bottom: 12px;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.provider-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.info-label {
  color: var(--el-text-color-secondary);
}

.info-value {
  color: var(--el-text-color-primary);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-value.mono {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 12px;
}

.card-actions {
  display: flex;
  gap: 4px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px 20px;
}

/* Dialog Styles */
.models-input-container {
  width: 100%;
}

.models-list-input {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  padding: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  min-height: 40px;
}

.model-tag-input {
  margin: 0;
}

.model-input {
  flex: 1;
  min-width: 150px;
}

.model-input :deep(.el-input__wrapper) {
  box-shadow: none;
  padding: 0;
}

@media (max-width: 768px) {
  .providers-page { padding: 16px; }
  .page-header { flex-direction: column; gap: 16px; }
  .provider-grid { grid-template-columns: 1fr; }
  .page-title { font-size: 24px; }
  .active-config-title { flex-direction: column; gap: 4px; }
  .active-config-inline { flex-direction: column; align-items: flex-start; }
}
</style>
