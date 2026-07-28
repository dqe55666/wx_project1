// pages/login/login.js
const app = getApp()

Page({
  data: {
    phone: '',
    password: '',
    showPassword: false,
    agreed: false,
    captchaPassed: false,
    submitting: false
  },

  onLoad() {
    // 已登录直接进主页；首次启动先看引导页
    if (app.globalData.loggedIn) {
      wx.switchTab({ url: '/pages/index/index' })
      return
    }
    if (app.globalData.needGuide) {
      wx.redirectTo({ url: '/pages/guide/guide' })
    }
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },

  togglePassword() {
    this.setData({ showPassword: !this.data.showPassword })
  },

  toggleAgree() {
    this.setData({ agreed: !this.data.agreed })
  },

  onCaptchaSuccess() {
    this.setData({ captchaPassed: true })
  },

  onCaptchaFail() {
    this.setData({ captchaPassed: false })
  },

  goForget() {
    wx.navigateTo({ url: '/pages/forget/forget' })
  },

  goRegister() {
    wx.navigateTo({ url: '/pages/register/register' })
  },

  onSubmit() {
    const { phone, password, agreed, captchaPassed } = this.data
    if (!phone || phone.length < 11) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!password) {
      wx.showToast({ title: '请输入密码', icon: 'none' })
      return
    }
    if (!captchaPassed) {
      wx.showToast({ title: '请先完成人机验证', icon: 'none' })
      return
    }
    if (!agreed) {
      wx.showToast({ title: '请先阅读并同意协议', icon: 'none' })
      return
    }
    // 壳子阶段：只展示 toast，然后跳转到主页
    this.setData({ submitting: true })
    wx.showLoading({ title: '登录中...', mask: true })
    setTimeout(() => {
      wx.hideLoading()
      this.setData({ submitting: false })
      // 记录登录态到本地与全局
      app.setLogin('mock-token-' + Date.now(), {
        phone: phone,
        name: '小陪用户',
        loginAt: Date.now()
      })
      // 标记引导页已读，避免下次再展示
      app.markGuideSeen && app.markGuideSeen()
      wx.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        wx.switchTab({ url: '/pages/index/index' })
      }, 600)
    }, 600)
  }
})
