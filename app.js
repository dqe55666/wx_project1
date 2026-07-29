// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 静默登录换取 code（壳子阶段不依赖后端）
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        console.info('[app] wx.login code', res.code)
      }
    })
  },

  globalData: {
    userInfo: null,
    apiBaseUrl: 'http://127.0.0.1:8000'
  }
})
