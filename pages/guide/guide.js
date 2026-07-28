// pages/guide/guide.js
const app = getApp()

Page({
  data: { current: 0 },
  onSwiperChange(e) { this.setData({ current: e.detail.current }) },
  goLogin() {
    // 跳转前先标记引导页已读，避免 login 再次跳回引导页
    app.markGuideSeen()
    wx.redirectTo({ url: '/pages/login/login' })
  },
  skip() {
    app.markGuideSeen()
    wx.redirectTo({ url: '/pages/login/login' })
  }
})
