Page({
  data: {
    name: '医用护理床',
    price: 1880,
    sales: 326,
    desc: '家用多功能护理床，可摇起、摇落、翻身，方便照顾卧床老人。'
  },
  goParam() { wx.navigateTo({ url: '/pages/mall/param' }) },
  goAddress() { wx.navigateTo({ url: '/pages/mall/address' }) },
  goCart() { wx.navigateTo({ url: '/pages/mall/confirm' }) },
  addToCart() {
    // 壳子阶段：弹个 toast 提示，留在商品页
    wx.showToast({ title: '已加入购物车（壳子）', icon: 'success' })
  },
  goMallHome() {
    wx.switchTab({ url: '/pages/mall/index', fail: () => wx.navigateBack({ delta: 1 }) })
  }
})
