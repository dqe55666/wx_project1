// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    const savedUserInfo = wx.getStorageSync('userInfo')
    if (savedUserInfo && savedUserInfo.nickName && savedUserInfo.avatarUrl) {
      this.globalData.userInfo = savedUserInfo
    }

    // 简易登录阶段仅保留登录 code，用户资料由用户主动授权后写入本地。
    wx.login({
      success: res => {
        this.globalData.loginCode = res.code
      }
    })
  },

  setUserInfo(userInfo) {
    const profile = {
      nickName: userInfo.nickName,
      avatarUrl: userInfo.avatarUrl
    }
    this.globalData.userInfo = profile
    this.globalData.loginPrompted = true
    wx.setStorageSync('userInfo', profile)
  },

  clearUserInfo() {
    this.globalData.userInfo = null
    this.globalData.loginPrompted = false
    wx.removeStorageSync('userInfo')
  },

  /**
   * 启动登录闸门：未登录时跳整屏登录页。
   * - 本次启动只提示一次（用户点「先随便看看」后不再重复打扰）
   * - 已登录直接返回，不闪页面
   * @returns {boolean} 是否触发了跳转
   */
  ensureLogin() {
    if (this.globalData.loginPrompted) {
      return false
    }
    const profile = this.globalData.userInfo
    if (profile && profile.nickName && profile.avatarUrl) {
      return false
    }
    this.globalData.loginPrompted = true
    const go = () => {
      wx.navigateTo({ url: '/pages/login/login' })
    }
    // 等首帧渲染完再跳，避免 navigateTo 时页面还没 ready
    if (wx.nextTick) {
      wx.nextTick(go)
    } else {
      setTimeout(go, 0)
    }
    return true
  },

  globalData: {
    userInfo: null,
    loginCode: '',
    loginPrompted: false,
    apiBaseUrl: 'http://127.0.0.1:8000'
  }
})
