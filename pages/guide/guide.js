const app = getApp()

Page({
  data: { current: 0 },
  onSwiperChange(e) { this.setData({ current: e.detail.current }) },
  goLogin() {
    // 必须先标记已读，否则 login 的 onLoad 会再次跳回引导页
    app.markGuideSeen && app.markGuideSeen()
    wx.redirectTo({ url: '/pages/login/login' })
  },
  skip() {
    app.markGuideSeen && app.markGuideSeen()
    wx.redirectTo({ url: '/pages/login/login' })
  }
})
