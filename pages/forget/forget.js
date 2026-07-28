// pages/forget/forget.js
Page({
  data: {
    phone: '',
    password: '',
    confirmPassword: '',
    showPassword: false,
    showConfirm: false,
    captchaPassed: false,
    submitting: false
  },

  onPhoneInput(e) { this.setData({ phone: e.detail.value }) },
  onPasswordInput(e) { this.setData({ password: e.detail.value }) },
  onConfirmInput(e) { this.setData({ confirmPassword: e.detail.value }) },

  togglePassword() { this.setData({ showPassword: !this.data.showPassword }) },
  toggleConfirm() { this.setData({ showConfirm: !this.data.showConfirm }) },

  onCaptchaSuccess() { this.setData({ captchaPassed: true }) },
  onCaptchaFail() { this.setData({ captchaPassed: false }) },

  onSubmit() {
    const { phone, password, confirmPassword, captchaPassed } = this.data
    if (!phone || phone.length < 11) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!password || password.length < 6) {
      wx.showToast({ title: '密码至少 6 位', icon: 'none' })
      return
    }
    if (password !== confirmPassword) {
      wx.showToast({ title: '两次密码不一致', icon: 'none' })
      return
    }
    if (!captchaPassed) {
      wx.showToast({ title: '请先完成人机验证', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    wx.showLoading({ title: '提交中...', mask: true })
    setTimeout(() => {
      wx.hideLoading()
      this.setData({ submitting: false })
      wx.showToast({ title: '重置成功（壳子）', icon: 'success' })
      setTimeout(() => wx.navigateBack({ delta: 1 }), 800)
    }, 800)
  }
})
