const { fetchMallOrders } = require('../../utils/api')

Page({
  data: {
    tabs: ['全部', '待付款', '已支付'],
    current: 0,
    list: []
  },
  onShow() { this.loadOrders() },
  async loadOrders() {
    try {
      const orders = await fetchMallOrders()
      this.setData({ list: orders.map((order) => ({
        ...order,
        no: order.order_no,
        name: order.product_name,
        cover: order.product_cover,
        price: (order.unit_price_cents / 100).toFixed(2),
        count: order.quantity,
        status: order.status === 'paid' ? '已支付' : '待付款',
        statusIdx: order.status === 'paid' ? 2 : 1
      })) })
    } catch (err) {
      this.setData({ list: [] })
    }
  },
  switchTab(e) { this.setData({ current: e.currentTarget.dataset.i }) },
  goDetail(e) {
    const id = e.currentTarget.dataset.id
    const order = this.data.list.find((item) => item.id === id)
    if (order) wx.navigateTo({ url: `/pages/mall/checkout?id=${order.id}&token=${encodeURIComponent(order.token)}` })
  },
  continuePay(e) {
    const order = this.data.list.find((item) => item.id === e.currentTarget.dataset.id)
    if (order) wx.navigateTo({ url: `/pages/mall/pay?id=${order.id}&token=${encodeURIComponent(order.token)}` })
  }
})
