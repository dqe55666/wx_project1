Page({
  data: {
    statusBarHeight: 20,
    agreed: false,
    authorizing: false
  },

  onLoad() {
    const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync()
    this.setData({ statusBarHeight: info.statusBarHeight || 20 })
  },

  toggleAgree() {
    this.setData({ agreed: !this.data.agreed })
  },

  openAgreement() {
    wx.showToast({ title: '用户协议内容准备中', icon: 'none' })
  },

  openPrivacy() {
    wx.showToast({ title: '隐私政策内容准备中', icon: 'none' })
  },

  onLogin() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先阅读并同意协议', icon: 'none' })
      return
    }
    if (this.data.authorizing) {
      return
    }
    if (!wx.getUserProfile) {
      wx.showToast({ title: '当前微信版本不支持授权', icon: 'none' })
      return
    }
    this.setData({ authorizing: true })
    wx.getUserProfile({
      desc: '用于展示您的微信昵称和头像',
      success: (result) => {
        const profile = result.userInfo || {}
        if (!profile.nickName || !profile.avatarUrl) {
          wx.showToast({ title: '未获取到完整用户资料', icon: 'none' })
          return
        }
        getApp().setUserInfo(profile)
        wx.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => this.leave(), 600)
      },
      fail: () => {
        wx.showToast({ title: '已取消微信授权', icon: 'none' })
      },
      complete: () => this.setData({ authorizing: false })
    })
  },

  onGuest() {
    this.leave()
  },

  onBack() {
    this.leave()
  },

  leave() {
    if (getCurrentPages().length > 1) {
      wx.navigateBack()
    } else {
      wx.switchTab({ url: '/pages/index/index' })
    }
  }
})
