Page({
  data: { form: { name: '', phone: '', idcard: '', city: '', intro: '' } },
  onInput(e) { this.setData({ [`form.${e.currentTarget.dataset.f}`]: e.detail.value }) },
  submit() {
    if (!this.data.form.name || !this.data.form.phone) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }
    wx.showLoading({ title: '提交中...' })
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({ title: '申请已提交（壳子）', icon: 'success' })
    }, 600)
  }
})
