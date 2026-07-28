// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 首次启动：未看过引导页则标记需要显示
    const sawGuide = wx.getStorageSync('sawGuide')
    if (!sawGuide) {
      this.globalData.needGuide = true
    }

    // 检查本地登录态
    const token = wx.getStorageSync('token')
    const user = wx.getStorageSync('user')
    if (token && user) {
      this.globalData.token = token
      this.globalData.userInfo = user
      this.globalData.loggedIn = true
    }

    // 静默登录换取 code（壳子阶段不依赖后端）
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        console.info('[app] wx.login code', res.code)
      }
    })
  },

  // 全局：跳到登录页（用于拦截需要登录的入口）
  requireLogin() {
    if (this.globalData.loggedIn) return true
    wx.showToast({ title: '请先登录', icon: 'none' })
    setTimeout(() => {
      wx.redirectTo({ url: '/pages/login/login' })
    }, 400)
    return false
  },

  // 全局：保存登录信息
  setLogin(token, user) {
    this.globalData.token = token
    this.globalData.userInfo = user
    this.globalData.loggedIn = true
    wx.setStorageSync('token', token)
    wx.setStorageSync('user', user)
  },

  // 全局：退出登录
  clearLogin() {
    this.globalData.token = ''
    this.globalData.userInfo = null
    this.globalData.loggedIn = false
    wx.removeStorageSync('token')
    wx.removeStorageSync('user')
  },

  // 标记引导页已读
  markGuideSeen() {
    this.globalData.needGuide = false
    wx.setStorageSync('sawGuide', true)
  },

  globalData: {
    userInfo: null,
    token: '',
    loggedIn: false,
    needGuide: false,
    apiBaseUrl: 'http://127.0.0.1:8000'
  }
})
