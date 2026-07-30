const { fetchCustomerOrder, getSavedOrder, request } = require('../../utils/api')

Page({
  data: {
    rating: 5,
    tags: [],
    content: '',
    tagOptions: ['专业耐心', '准时到达', '细致入微', '服务热情', '经验丰富', '沟通顺畅'],
    order: null,
    submitting: false
  },

  onLoad(options) {
    this.orderId = Number(options.id)
    this.loadOrder()
  },

  async loadOrder() {
    const saved = getSavedOrder(this.orderId)
    if (!saved) return
    try {
      const order = await fetchCustomerOrder(saved)
      this.setData({ order })
    } catch (err) {
      wx.showToast({ title: err.detail || '订单加载失败', icon: 'none' })
    }
  },

  setRating(e) {
    this.setData({ rating: Number(e.currentTarget.dataset.r) })
  },

  toggleTag(e) {
    const t = e.currentTarget.dataset.t
    const list = this.data.tags.includes(t)
      ? this.data.tags.filter(x => x !== t)
      : [...this.data.tags, t]
    this.setData({ tags: list })
  },

  onInput(e) {
    this.setData({ content: e.detail.value })
  },

  async submit() {
    const saved = getSavedOrder(this.orderId)
    if (!saved) {
      wx.showToast({ title: '订单凭据已失效', icon: 'none' })
      return
    }
    const content = [...this.data.tags, this.data.content.trim()].filter(Boolean).join('；')
    if (!content) {
      wx.showToast({ title: '请填写评价内容', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    try {
      await request(`/api/customer/orders/${this.orderId}/review?token=${encodeURIComponent(saved.token)}`, {
        method: 'POST',
        data: { rating: this.data.rating, content }
      })
      wx.showToast({ title: '评价成功', icon: 'success' })
      setTimeout(() => wx.navigateBack({ delta: 1 }), 600)
    } catch (err) {
      wx.showToast({ title: err.detail || '评价失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  }
})
