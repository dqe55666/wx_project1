const { fetchCustomerOrders, fetchCustomerOrderMessages, getSavedOrder, formatDateTime } = require('../../utils/api')

Page({
  data: {
    list: [],
    loading: false
  },

  onShow() {
    this.loadMessages()
  },

  async loadMessages() {
    this.setData({ loading: true })
    try {
      const orders = await fetchCustomerOrders()
      const list = await Promise.all(orders.map(async (order) => {
        let latest = null
        const saved = getSavedOrder(order.id)
        if (saved) {
          try {
            const messages = await fetchCustomerOrderMessages(saved)
            latest = messages[messages.length - 1] || null
          } catch (err) {
            latest = null
          }
        }
        return {
          id: `order-${order.id}`,
          avatar: order.employee_name ? '护' : '单',
          name: order.employee_name || '订单通知',
          desc: latest ? latest.content : `${order.statusText} · ${order.hospital}`,
          time: latest ? formatDateTime(latest.created_at) : (order.appointmentDisplay || ''),
          unread: order.canReview ? 1 : 0
        }
      }))
      if (orders.length) {
        list.unshift({
          id: 'system',
          avatar: '知',
          name: '系统通知',
          desc: `本机共有 ${orders.length} 条预约记录`,
          time: '',
          unread: 0
        })
      }
      this.setData({ list })
    } catch (err) {
      wx.showToast({ title: '消息加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  goChat(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/message/chat?id=' + id })
  },

  goNotice() {
    wx.navigateTo({ url: '/pages/message/chat?id=system' })
  },

  goCalendar() {
    wx.switchTab({ url: '/pages/visit/list', fail: () => wx.navigateTo({ url: '/pages/visit/list' }) })
  },

  goMall() {
    wx.switchTab({ url: '/pages/mall/index', fail: () => wx.navigateTo({ url: '/pages/mall/index' }) })
  },

  goOrders() {
    wx.navigateTo({ url: '/pages/mine/orders' })
  }
})
