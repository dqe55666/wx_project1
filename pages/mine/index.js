const { fetchCustomerOrders } = require('../../utils/api')

Page({
  data: {
    user: { name: '未登录', phone: '授权后可展示昵称和头像', level: '游客模式', avatarUrl: '' },
    loggedIn: false,
    authorizing: false,
    loginButtonText: '微信授权登录',
    orderCount: { pending: 0, doing: 0, evaluate: 0, refund: 0 },
    menus: [
      { id: 'apply', icon: '👩‍⚕️', name: '陪诊师入驻' },
      { id: 'orders', icon: '📋', name: '我的订单' },
      { id: 'mall', icon: '🛍️', name: '商城订单' },
      { id: 'wallet', icon: '💰', name: '我的钱包' },
      { id: 'coupon', icon: '🎟️', name: '优惠券' },
      { id: 'address', icon: '📍', name: '收货地址' },
      { id: 'collect', icon: '⭐', name: '我的收藏' },
      { id: 'history', icon: '🕘', name: '浏览历史' },
      { id: 'service', icon: '🎧', name: '在线客服' },
      { id: 'feedback', icon: '📝', name: '意见反馈' },
      { id: 'about', icon: 'ℹ️', name: '关于我们' },
      { id: 'setting', icon: '⚙️', name: '设置' }
    ]
  },

  onShow() {
    this.syncUserInfo()
    this.loadOrderCount()
  },

  syncUserInfo() {
    const app = getApp()
    const profile = app.globalData.userInfo || wx.getStorageSync('userInfo')
    const loggedIn = Boolean(profile && profile.nickName && profile.avatarUrl)
    this.setData({
      loggedIn,
      loginButtonText: loggedIn ? '重新授权' : '微信授权登录',
      user: loggedIn
        ? { name: profile.nickName, avatarUrl: profile.avatarUrl, phone: '微信授权登录', level: '已登录' }
        : { name: '未登录', phone: '授权后可展示昵称和头像', level: '游客模式', avatarUrl: '' }
    })
  },

  authorizeLogin() {
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
        this.syncUserInfo()
        wx.showToast({ title: '登录成功', icon: 'success' })
      },
      fail: () => {
        wx.showToast({ title: '已取消微信授权', icon: 'none' })
      },
      complete: () => this.setData({ authorizing: false })
    })
  },

  async loadOrderCount() {
    try {
      const orders = await fetchCustomerOrders()
      this.setData({
        orderCount: {
          pending: orders.filter((item) => item.rawStatus === 'pending').length,
          doing: orders.filter((item) => item.rawStatus === 'accepted' || item.rawStatus === 'in_progress').length,
          evaluate: orders.filter((item) => item.canReview).length,
          refund: 0
        }
      })
    } catch (err) {
      this.setData({ orderCount: { pending: 0, doing: 0, evaluate: 0, refund: 0 } })
    }
  },

  goMenu(e) {
    const id = e.currentTarget.dataset.id
    const map = {
      apply: '/pages/mine/apply',
      orders: '/pages/mine/orders',
      mall: '/pages/mine/mall-orders',
      address: '/pages/mall/address',
      service: '/pages/support/chat',
      feedback: '/pages/support/feedback',
      setting: '/pages/mine/setting'
    }
    if (map[id]) {
      wx.navigateTo({ url: map[id] })
    } else {
      wx.showToast({ title: '功能开发中', icon: 'none' })
    }
  },

  goOrder(e) {
    const type = e.currentTarget.dataset.type
    const map = {
      pending: { url: '/pages/mine/orders?type=pending' },
      doing: { url: '/pages/visit/list' },
      evaluate: { url: '/pages/mine/orders?type=evaluate' },
      refund: { url: '/pages/mine/refund' },
      all: { url: '/pages/mine/orders' }
    }
    if (map[type]) {
      wx.switchTab({ url: map[type].url, fail: () => wx.navigateTo({ url: map[type].url }) })
    }
  }
})
