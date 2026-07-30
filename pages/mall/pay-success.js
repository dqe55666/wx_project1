Page({
  data: { orderId: 0, token: '' },
  onLoad(options) { this.setData({ orderId: Number(options.id), token: options.token || '' }) },
  goOrders() { wx.navigateTo({ url: '/pages/mine/mall-orders' }) },
  goHome() { wx.switchTab({ url: '/pages/index/index' }) }
})
