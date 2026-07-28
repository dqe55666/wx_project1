Page({
  goOrders() { wx.switchTab({ url: '/pages/mine/index', fail: () => wx.navigateBack({ delta: 2 }) }) },
  goHome() { wx.switchTab({ url: '/pages/index/index' }) }
})
