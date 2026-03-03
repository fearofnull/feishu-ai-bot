import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GlobalLoading from '@/components/GlobalLoading.vue'

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  Loading: { name: 'Loading' }
}))

describe('GlobalLoading.vue', () => {
  it('renders loading overlay when visible is true', () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: true
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.global-loading-overlay').exists()).toBe(true)
  })

  it('does not render loading overlay when visible is false', () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: false
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.global-loading-overlay').exists()).toBe(false)
  })

  it('displays default loading message', () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: true
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.loading-text').text()).toBe('加载中...')
  })

  it('displays custom loading message', () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: true,
        message: '正在保存配置...'
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.loading-text').text()).toBe('正在保存配置...')
  })

  it('renders loading icon', () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: true
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.loading-icon').exists()).toBe(true)
  })

  it('has correct overlay styling classes', () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: true
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.global-loading-overlay').exists()).toBe(true)
    expect(wrapper.find('.loading-content').exists()).toBe(true)
  })

  it('applies fade transition', () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: true
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    // Check that transition wrapper exists
    const transition = wrapper.findComponent({ name: 'Transition' })
    expect(transition.exists()).toBe(true)
    expect(transition.props('name')).toBe('fade')
  })

  it('updates message when prop changes', async () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: true,
        message: '初始消息'
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.loading-text').text()).toBe('初始消息')

    await wrapper.setProps({ message: '更新后的消息' })

    expect(wrapper.find('.loading-text').text()).toBe('更新后的消息')
  })

  it('shows and hides overlay when visible prop changes', async () => {
    const wrapper = mount(GlobalLoading, {
      props: {
        visible: false
      },
      global: {
        stubs: {
          'el-icon': {
            template: '<i class="el-icon"><slot /></i>',
            props: ['size']
          }
        }
      }
    })

    expect(wrapper.find('.global-loading-overlay').exists()).toBe(false)

    await wrapper.setProps({ visible: true })

    expect(wrapper.find('.global-loading-overlay').exists()).toBe(true)

    await wrapper.setProps({ visible: false })

    expect(wrapper.find('.global-loading-overlay').exists()).toBe(false)
  })
})
