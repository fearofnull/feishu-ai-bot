import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '@/components/HelloWorld.vue'

describe('HelloWorld.vue', () => {
  it('renders message prop when passed', () => {
    const msg = 'Test Message'
    const wrapper = mount(HelloWorld, {
      props: { msg }
    })
    
    expect(wrapper.text()).toContain(msg)
  })

  it('renders with default structure', () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Hello' }
    })
    
    expect(wrapper.find('h1').exists()).toBe(true)
    expect(wrapper.find('.card').exists()).toBe(true)
  })

  it('increments count when button is clicked', async () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Test' }
    })
    
    const button = wrapper.find('button')
    expect(button.text()).toContain('count is 0')
    
    await button.trigger('click')
    expect(button.text()).toContain('count is 1')
    
    await button.trigger('click')
    expect(button.text()).toContain('count is 2')
  })

  it('displays correct initial count', () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Test' }
    })
    
    expect(wrapper.text()).toContain('count is 0')
  })

  it('contains documentation links', () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Test' }
    })
    
    const links = wrapper.findAll('a')
    expect(links.length).toBeGreaterThan(0)
  })
})
