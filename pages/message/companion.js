const { fetchCustomerOrder, getSavedOrder } = require('../../utils/api')

Page({
  data: {
    name: '待接单',
    level: '陪诊师接单后显示资料',
    score: '-',
    orders: '-',
    intro: '当前后端已提供员工姓名与电话，更多陪诊师档案可后续补充。',
    hospitals: []
  },

  onLoad(options) {
    this.orderId = Number(options.id)
    this.loadCompanion()
  },

  async loadCompanion() {
    const saved = getSavedOrder(this.orderId)
    if (!saved) return
    try {
      const order = await fetchCustomerOrder(saved)
      this.setData({
        name: order.employee_name || '待接单',
        level: order.employee_name ? '已接单陪诊师' : '等待陪诊师接单',
        score: order.employee_name ? '5.0' : '-',
        orders: order.employee_name ? '1' : '-',
        intro: order.employee_name
          ? `${order.employee_name} 将为您提供 ${order.typeName} 服务。`
          : '接单后可在这里查看陪诊师信息。',
        hospitals: [order.hospital].filter(Boolean)
      })
    } catch (err) {
      wx.showToast({ title: '陪诊师资料加载失败', icon: 'none' })
    }
  }
})
