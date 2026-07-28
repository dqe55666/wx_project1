Page({
  data: {
    savedOrderCount: 0
  },

  onShow() {
    const savedOrders = wx.getStorageSync('customerOrders') || []
    this.setData({ savedOrderCount: savedOrders.length })
  },

  openOrders() {
    wx.navigateTo({ url: '/pages/orders/orders' })
  },

  openBooking() {
    wx.navigateTo({ url: '/pages/booking/booking' })
  }
})
