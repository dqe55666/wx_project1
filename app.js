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
    wx.setStorageSync('userInfo', profile)
  },

  clearUserInfo() {
    this.globalData.userInfo = null
    wx.removeStorageSync('userInfo')
  },

  globalData: {
    userInfo: null,
    loginCode: '',
    apiBaseUrl: 'http://127.0.0.1:8000'
  }
})
