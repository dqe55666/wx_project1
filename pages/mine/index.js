Page({
  data: {
    user: { name: '小陪用户', phone: '188****5678', level: 'VIP会员' },
    orderCount: { paying: 0, doing: 1, evaluate: 1, refund: 0 },
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

  goMenu(e) {
    const id = e.currentTarget.dataset.id
    const map = {
      apply: '/pages/mine/apply',
      orders: '/pages/mine/orders',
      mall: '/pages/mine/mall-orders',
      address: '/pages/mall/address',
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
      paying: { url: '/pages/mine/orders?type=paying', title: '待支付' },
      doing: { url: '/pages/visit/list', title: '进行中' },
      evaluate: { url: '/pages/mine/orders?type=evaluate', title: '待评价' },
      refund: { url: '/pages/mine/refund', title: '退款' }
    }
    if (map[type]) {
      wx.switchTab({ url: map[type].url, fail: () => wx.navigateTo({ url: map[type].url }) })
    }
  }
})
