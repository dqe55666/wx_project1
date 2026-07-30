const { fetchCustomerOrders } = require('../../utils/api')

Page({
  data: {
    tabs: ['全部', '待接单', '进行中', '待评价'],
    current: 0,
    list: [],
    loading: false
  },

  onLoad(options) {
    const typeMap = { pending: 1, doing: 2, evaluate: 3 }
    if (options.type && typeMap[options.type]) {
      this.setData({ current: typeMap[options.type] })
    }
  },

  onShow() {
    this.loadOrders()
  },

  async loadOrders() {
    this.setData({ loading: true })
    try {
      const list = await fetchCustomerOrders()
      this.setData({ list })
    } catch (err) {
      wx.showToast({ title: '订单加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  switchTab(e) {
    this.setData({ current: e.currentTarget.dataset.i })
  },

  goDetail(e) {
    wx.navigateTo({ url: '/pages/visit/detail?id=' + e.currentTarget.dataset.id })
  }
})
