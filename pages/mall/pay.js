const { request, fetchMallOrder, getSavedMallOrder } = require('../../utils/api')

Page({
  data: {
    amount: '0.00',
    order: null,
    paying: false,
    payType: 0,
    payTypes: [
      { id: 0, name: '微信支付', icon: '💚' },
      { id: 1, name: '余额支付', icon: '💰' }
    ]
  },
  onLoad(options) {
    this.orderId = Number(options.id)
    this.token = options.token || (getSavedMallOrder(this.orderId) || {}).token
    this.loadOrder()
  },
  async loadOrder() {
    if (!this.orderId || !this.token) return
    try {
      const order = await fetchMallOrder({ id: this.orderId, token: this.token })
      this.setData({ order, amount: (order.amount_cents / 100).toFixed(2) })
      if (order.status === 'paid') this.goSuccess()
    } catch (err) {
      wx.showToast({ title: '订单不存在或已失效', icon: 'none' })
    }
  },
  pickType(e) { this.setData({ payType: e.currentTarget.dataset.i }) },
  async pay() {
    if (this.data.paying) return
    if (!this.orderId || !this.token || !this.data.order) {
      wx.showToast({ title: '订单信息无效', icon: 'none' })
      return
    }
    this.setData({ paying: true })
    wx.showLoading({ title: '支付中...' })
    try {
      await request(`/api/mall/orders/${this.orderId}/pay?token=${encodeURIComponent(this.token)}`, {
        method: 'POST',
      })
      wx.hideLoading()
      this.goSuccess()
    } catch (err) {
      wx.hideLoading()
      this.setData({ paying: false })
      wx.showToast({ title: (err && err.detail) || '商品库存不足，请返回商城刷新', icon: 'none' })
    }
  },
  goSuccess() {
    wx.redirectTo({ url: `/pages/mall/pay-success?id=${this.orderId}&token=${encodeURIComponent(this.token)}` })
  }
})
