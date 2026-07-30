const { fetchMallOrder, getSavedMallOrder } = require('../../utils/api')

Page({
  data: {
    order: null,
    loading: true
  },
  onLoad(options) {
    this.orderId = Number(options.id)
    this.token = options.token || (getSavedMallOrder(this.orderId) || {}).token
    this.loadOrder()
  },
  async loadOrder() {
    if (!this.orderId || !this.token) {
      wx.showToast({ title: '订单凭据无效', icon: 'none' })
      return
    }
    try {
      const order = await fetchMallOrder({ id: this.orderId, token: this.token })
      this.setData({
        order: {
          ...order,
          amount: (order.amount_cents / 100).toFixed(2),
          unitPrice: (order.unit_price_cents / 100).toFixed(2),
          createdAt: order.created_at.replace('T', ' ').slice(0, 16),
          isPaid: order.status === 'paid'
        },
        loading: false
      })
    } catch (err) {
      this.setData({ loading: false })
      wx.showToast({ title: '订单不存在或已失效', icon: 'none' })
    }
  },
  goPay() {
    const order = this.data.order
    if (!order || order.isPaid) return
    wx.navigateTo({ url: `/pages/mall/pay?id=${order.id}&token=${encodeURIComponent(this.token)}` })
  }
})
