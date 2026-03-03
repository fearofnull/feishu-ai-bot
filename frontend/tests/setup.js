import { vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

global.localStorage = localStorageMock

// Reset localStorage before each test
beforeEach(() => {
  localStorageMock.getItem.mockImplementation((key) => {
    return localStorageMock[key] || null
  })
  localStorageMock.setItem.mockImplementation((key, value) => {
    localStorageMock[key] = value
  })
  localStorageMock.removeItem.mockImplementation((key) => {
    delete localStorageMock[key]
  })
  localStorageMock.clear.mockImplementation(() => {
    Object.keys(localStorageMock).forEach(key => {
      if (key !== 'getItem' && key !== 'setItem' && key !== 'removeItem' && key !== 'clear') {
        delete localStorageMock[key]
      }
    })
  })
})

// Common Element Plus component stubs for testing
export const elementPlusStubs = {
  'el-form': {
    template: '<form ref="formRef"><slot /></form>',
    methods: {
      validate: vi.fn().mockResolvedValue(true),
      clearValidate: vi.fn(),
      resetFields: vi.fn()
    }
  },
  'el-form-item': {
    template: '<div class="el-form-item"><label><slot name="label" /></label><slot /><div class="extra"><slot name="extra" /></div></div>',
    props: ['label', 'prop']
  },
  'el-input': {
    template: '<input type="text" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" :placeholder="placeholder" />',
    props: ['modelValue', 'placeholder', 'clearable', 'type', 'showPassword']
  },
  'el-select': {
    template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
    props: ['modelValue', 'placeholder', 'clearable', 'filterable']
  },
  'el-option': {
    template: '<option :value="value"><slot /></option>',
    props: ['label', 'value']
  },
  'el-button': {
    template: '<button @click="$attrs.onClick" :disabled="loading || disabled" :type="nativeType"><slot /></button>',
    props: ['type', 'loading', 'disabled', 'icon', 'nativeType', 'plain', 'round', 'circle']
  },
  'el-alert': {
    template: '<div class="el-alert" :class="`el-alert--${type}`"><slot /></div>',
    props: ['title', 'type', 'closable', 'showIcon', 'description']
  },
  'el-icon': {
    template: '<i class="el-icon"><slot /></i>',
    props: ['size', 'color']
  },
  'el-card': {
    template: '<div class="el-card"><div class="card-header"><slot name="header" /></div><slot /></div>',
    props: ['shadow', 'bodyStyle']
  },
  'el-descriptions': {
    template: '<div class="el-descriptions"><slot /></div>',
    props: ['column', 'border', 'size', 'direction']
  },
  'el-descriptions-item': {
    template: '<div class="el-descriptions-item"><div class="label"><slot name="label" /></div><div class="content"><slot /></div></div>',
    props: ['label', 'span']
  },
  'el-tag': {
    template: '<span class="el-tag" :class="`el-tag--${type}`"><slot /></span>',
    props: ['type', 'size', 'effect', 'round', 'closable']
  },
  'el-empty': {
    template: '<div class="el-empty"><slot name="image" /><div class="el-empty__description"><slot /></div></div>',
    props: ['description', 'imageSize']
  },
  'el-table': {
    template: '<table class="el-table"><slot /></table>',
    props: ['data', 'stripe', 'border', 'size', 'loading', 'rowClassName']
  },
  'el-table-column': {
    template: '<td><slot /></td>',
    props: ['prop', 'label', 'width', 'minWidth', 'align', 'sortable', 'fixed']
  },
  'el-radio-group': {
    template: '<div class="el-radio-group"><slot /></div>',
    props: ['modelValue', 'size']
  },
  'el-radio-button': {
    template: '<button class="el-radio-button" @click="$emit(\'click\')"><slot /></button>',
    props: ['label', 'value']
  },
  'el-dialog': {
    template: '<div v-if="modelValue" class="el-dialog"><div class="el-dialog__header"><slot name="header" /></div><div class="el-dialog__body"><slot /></div><div class="el-dialog__footer"><slot name="footer" /></div></div>',
    props: ['modelValue', 'title', 'width', 'beforeClose']
  },
  'el-container': {
    template: '<div class="el-container"><slot /></div>'
  },
  'el-header': {
    template: '<header class="el-header"><slot /></header>',
    props: ['height']
  },
  'el-main': {
    template: '<main class="el-main"><slot /></main>'
  }
}
