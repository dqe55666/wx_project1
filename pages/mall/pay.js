Page({
  data: {
    amount: 1880,
    payType: 0,
    payTypes: [
      { id: 0, name: '微信支付', icon: '💚' },
      { id: 1, name: '余额支付', icon: '💰' }
    ]
  },
  pickType(e) { this.setData({ payType: e.currentTarget.dataset.i }) },
  pay() {
    wx.showLoading({ title: '支付中...' })
    setTimeout(() => {
      wx.hideLoading()
      wx.redirectTo({ url: '/pages/mall/pay-success' })
    }, 800)
  }
})
