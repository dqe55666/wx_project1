const {
  fetchCustomerOrder,
  fetchCustomerOrderMessages,
  getSavedOrder,
  formatDateTime
} = require('../../utils/api')

Page({
  data: {
    kw: '',
    source: [],
    results: []
  },

  onLoad(options) {
    this.chatId = options.id || ''
    this.loadSource()
  },

  async loadSource() {
    const orderId = Number((this.chatId || '').replace('order-', ''))
    const saved = getSavedOrder(orderId)
    if (!saved) return
    try {
      const order = await fetchCustomerOrder(saved)
      const messages = await fetchCustomerOrderMessages(saved)
      this.setData({
        source: [
          { id: 1, text: `${order.typeName}预约：${order.statusText}`, time: order.appointmentDisplay },
          { id: 2, text: `${order.hospital} ${order.address}`, time: order.appointmentDisplay },
          ...messages.map((message) => ({
            id: `msg-${message.id}`,
            text: message.content,
            time: formatDateTime(message.created_at)
          }))
        ]
      })
    } catch (err) {
      wx.showToast({ title: '记录加载失败', icon: 'none' })
    }
  },

  onInput(e) {
    const kw = e.detail.value.trim()
    const results = kw
      ? this.data.source.filter((item) => item.text.indexOf(kw) >= 0)
      : []
    this.setData({ kw, results })
  }
})
