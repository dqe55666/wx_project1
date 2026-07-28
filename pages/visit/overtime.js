Page({
  data: { hours: 1, price: 100 },
  changeHours(e) {
    const h = Number(e.currentTarget.dataset.h)
    this.setData({ hours: h, price: h * 100 })
  },
  confirm() {
    wx.showLoading({ title: '支付中...' })
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({ title: '加时成功（壳子）', icon: 'success' })
      setTimeout(() => wx.navigateBack({ delta: 1 }), 600)
    }, 500)
  }
})
