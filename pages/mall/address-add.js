Page({
  data: {
    form: { name: '', phone: '', region: '', detail: '', tag: '' },
    default: false
  },
  onInput(e) { this.setData({ [`form.${e.currentTarget.dataset.f}`]: e.detail.value }) },
  toggleDefault() { this.setData({ default: !this.data.default }) },
  save() {
    if (!this.data.form.name || !this.data.form.phone) {
      wx.showToast({ title: '请填写完整', icon: 'none' })
      return
    }
    wx.showToast({ title: '已保存（壳子）', icon: 'success' })
    setTimeout(() => wx.navigateBack({ delta: 1 }), 600)
  }
})
