Page({
  data: { reason: '' },
  onReason(e) { this.setData({ reason: e.detail.value }) },
  confirm() {
    if (!this.data.reason) { wx.showToast({ title: '请填写结束原因', icon: 'none' }); return }
    wx.showLoading({ title: '提交中...' })
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({ title: '已结束（壳子）', icon: 'success' })
      setTimeout(() => wx.navigateBack({ delta: 1 }), 600)
    }, 500)
  }
})
