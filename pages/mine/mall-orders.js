Page({
  data: {
    tabs: ['全部', '待付款', '待发货', '待收货', '已完成'],
    current: 0,
    list: [
      { id: 1, no: 'SO' + Date.now(), name: '医用护理床', cover: '🛏️', price: 1880, count: 1, status: '待发货', statusIdx: 2 },
      { id: 2, no: 'SO' + (Date.now() - 86400000), name: '血压计（家用手腕式）', cover: '🩺', price: 268, count: 1, status: '待评价', statusIdx: 4 }
    ]
  },
  switchTab(e) { this.setData({ current: e.currentTarget.dataset.i }) },
  goDetail(e) {
    // 商城订单详情复用订单确认页
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/mall/checkout?id=' + id })
  },
  goEvaluate() { wx.navigateTo({ url: '/pages/mine/evaluate' }) },
  goRefund() { wx.navigateTo({ url: '/pages/mine/refund' }) }
})
