const app = getApp()

Page({
  data: { push: true, face: false },
  togglePush() { this.setData({ push: !this.data.push }) },
  toggleFace() { this.setData({ face: !this.data.face }) },
  goAccount() { wx.showToast({ title: '账号信息（壳子）', icon: 'none' }) },
  goChangePwd() { wx.navigateTo({ url: '/pages/forget/forget' }) },
  goPrivacy() { wx.showToast({ title: '隐私设置（壳子）', icon: 'none' }) },
  goClearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定清除本地缓存吗？',
      success: r => r.confirm && wx.showToast({ title: '已清除', icon: 'success' })
    })
  },
  goAbout() { wx.showToast({ title: '关于我们（壳子）', icon: 'none' }) },
  goCheckUpdate() { wx.showToast({ title: '已是最新版本', icon: 'none' }) },
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      success: r => {
        if (r.confirm) {
          app.clearLogin()
          wx.showToast({ title: '已退出', icon: 'success' })
          setTimeout(() => {
            wx.reLaunch({ url: '/pages/login/login' })
          }, 600)
        }
      }
    })
  }
})
