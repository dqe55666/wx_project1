Page({
  data: { push: true, face: false },
  togglePush() { this.setData({ push: !this.data.push }) },
  toggleFace() { this.setData({ face: !this.data.face }) },
  goAccount() {
    const profile = getApp().globalData.userInfo || wx.getStorageSync('userInfo')
    wx.showModal({
      title: '账号信息',
      content: profile && profile.nickName ? `微信昵称：${profile.nickName}` : '当前为游客模式，前往“我的”页面完成微信授权登录。',
      showCancel: false
    })
  },
  goChangePwd() { wx.showToast({ title: '修改密码（壳子）', icon: 'none' }) },
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
          getApp().clearUserInfo()
          wx.showToast({ title: '已退出登录', icon: 'success' })
        }
      }
    })
  }
})
