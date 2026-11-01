// 微信已收回 wx.getUserProfile（新基础库拿到的都是灰色头像 +「微信用户」），
// 改用官方「头像昵称填写能力」：button open-type="chooseAvatar" + input type="nickname"
const DEFAULT_AVATAR = '/assets/images/avatar-default.png'

Page({
  data: {
    statusBarHeight: 20,
    agreed: false,
    avatarUrl: DEFAULT_AVATAR,
    avatarPicked: false,
    nickname: ''
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

  onChooseAvatar(e) {
    const url = e.detail && e.detail.avatarUrl
    if (!url) {
      return
    }
    this.setData({ avatarUrl: url, avatarPicked: true })
  },

  onNickInput(e) {
    this.setData({ nickname: e.detail.value })
  },

  onLogin() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先阅读并同意协议', icon: 'none' })
      return
    }
    const nick = (this.data.nickname || '').trim()
    if (!nick) {
      wx.showToast({ title: '请填写您的昵称', icon: 'none' })
      return
    }
    getApp().setUserInfo({ nickName: nick, avatarUrl: this.data.avatarUrl })
    wx.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => this.leave(), 600)
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
