const app = getApp()

Page({
  data: {
    orders: [],
    loading: false,
    activeReviewId: null,
    reviewRating: 5,
    reviewContent: '',
    submittingReview: false
  },

  onShow() {
    this.loadOrders()
  },

  request(path, options = {}) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBaseUrl}${path}`,
        method: options.method || 'GET',
        data: options.data,
        header: { 'content-type': 'application/json' },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
            return
          }
          reject(res.data || {})
        },
        fail: reject
      })
    })
  },

  async loadOrders() {
    const savedOrders = wx.getStorageSync('customerOrders') || []
    if (!savedOrders.length) {
      this.setData({ orders: [], loading: false })
      return
    }
    this.setData({ loading: true })
    const orders = await Promise.all(savedOrders.map(async (saved) => {
      try {
        const order = await this.request(`/api/customer/orders/${saved.id}?token=${encodeURIComponent(saved.token)}`)
        return {
          ...order,
          appointmentDisplay: order.appointment_time.replace('T', ' ').slice(0, 16),
          statusText: order.status_text || this.statusText(order.status, order.completion_type),
          canReview: order.status === 'completed' && !order.review
        }
      } catch (err) {
        return null
      }
    }))
    this.setData({
      orders: orders.filter(Boolean),
      loading: false
    })
  },

  statusText(status, completionType) {
    if (completionType === 'negotiated_early') return '经协商提前结束'
    if (completionType === 'system_confirmed') return '由系统确认，订单结束'
    return {
      pending: '待接单',
      accepted: '已接单',
      in_progress: '服务中',
      completed: '服务已完成',
      stopped: '订单已停止'
    }[status] || status
  },

  openTracking(e) {
    const orderId = Number(e.currentTarget.dataset.id)
    const saved = (wx.getStorageSync('customerOrders') || []).find((item) => item.id === orderId)
    if (!saved) {
      wx.showToast({ title: '订单凭据已失效', icon: 'none' })
      return
    }
    wx.navigateTo({
      url: `/pages/tracking/tracking?id=${orderId}&token=${encodeURIComponent(saved.token)}`
    })
  },

  openReview(e) {
    this.setData({
      activeReviewId: Number(e.currentTarget.dataset.id),
      reviewRating: 5,
      reviewContent: ''
    })
  },

  cancelReview() {
    this.setData({ activeReviewId: null, reviewContent: '' })
  },

  selectRating(e) {
    this.setData({ reviewRating: Number(e.currentTarget.dataset.rating) })
  },

  onReviewInput(e) {
    this.setData({ reviewContent: e.detail.value })
  },

  async submitReview() {
    const { activeReviewId, reviewRating, reviewContent } = this.data
    const content = reviewContent.trim()
    if (!content) {
      wx.showToast({ title: '请填写评价内容', icon: 'none' })
      return
    }
    const savedOrders = wx.getStorageSync('customerOrders') || []
    const saved = savedOrders.find((item) => item.id === activeReviewId)
    if (!saved) return
    this.setData({ submittingReview: true })
    try {
      await this.request(`/api/customer/orders/${activeReviewId}/review?token=${encodeURIComponent(saved.token)}`, {
        method: 'POST',
        data: { rating: reviewRating, content }
      })
      wx.showToast({ title: '评价已提交', icon: 'success' })
      this.setData({ activeReviewId: null, reviewContent: '' })
      this.loadOrders()
    } catch (err) {
      wx.showToast({ title: err.detail || '评价提交失败', icon: 'none' })
    } finally {
      this.setData({ submittingReview: false })
    }
  }
})
