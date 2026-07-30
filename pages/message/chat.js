const {
  fetchCustomerOrder,
  fetchCustomerOrderMessages,
  getSavedOrder,
  sendCustomerOrderMessage,
  formatDateTime
} = require('../../utils/api')

function systemMessagesForOrder(order) {
  return [
    {
      id: 'system-status',
      from: 'other',
      text: `您的${order.typeName}预约当前为：${order.statusText}`,
      time: order.appointmentDisplay || '系统'
    },
    {
      id: 'system-staff',
      from: 'other',
      text: order.employee_name
        ? `${order.employee_name} 已接单，可直接在这里沟通服务细节。`
        : '陪诊师接单后，可在这里和陪诊师沟通。',
      time: order.appointmentDisplay || '系统'
    }
  ]
}

function normalizeMessage(message) {
  return {
    id: `msg-${message.id}`,
    rawId: message.id,
    from: message.sender_type === 'customer' ? 'me' : 'other',
    text: message.content,
    time: formatDateTime(message.created_at) || '刚刚',
    senderName: message.sender_name
  }
}

Page({
  data: {
    name: '系统通知',
    input: '',
    msgs: [],
    sending: false,
    scrollIntoView: 'bottom'
  },

  onLoad(options) {
    this.chatId = options.id || 'system'
    this.orderId = 0
    this.saved = null
    this.systemMsgs = []
    this.lastMessageId = 0
    this.loadChat()
  },

  onUnload() {
    this.stopPolling()
  },

  async loadChat() {
    if (this.chatId === 'system') {
      this.setData({
        name: '系统通知',
        msgs: [
          { id: 1, from: 'other', text: '预约提交后，订单状态会在这里同步。', time: '系统' }
        ]
      })
      return
    }
    const orderId = Number(this.chatId.replace('order-', ''))
    const saved = getSavedOrder(orderId)
    if (!saved) {
      wx.showToast({ title: '未找到本机订单凭证', icon: 'none' })
      return
    }
    this.saved = saved
    this.orderId = orderId
    try {
      const order = await fetchCustomerOrder(saved)
      this.systemMsgs = systemMessagesForOrder(order)
      this.setData({
        name: order.employee_name || '订单通知',
        msgs: this.systemMsgs
      })
      await this.loadMessages()
      this.startPolling()
    } catch (err) {
      wx.showToast({ title: err.detail || '会话加载失败', icon: 'none' })
    }
  },

  startPolling() {
    this.stopPolling()
    this.pollTimer = setInterval(() => this.loadMessages(true), 5000)
  },

  stopPolling() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer)
      this.pollTimer = null
    }
  },

  scrollBottom() {
    this.setData({ scrollIntoView: '' }, () => {
      this.setData({ scrollIntoView: 'bottom' })
    })
  },

  async loadMessages(silent = false) {
    if (!this.saved) return
    try {
      const messages = await fetchCustomerOrderMessages(this.saved, this.lastMessageId)
      if (!messages.length) return
      const normalized = messages.map(normalizeMessage)
      this.lastMessageId = Math.max(this.lastMessageId, ...messages.map((item) => item.id))
      const existing = new Set(this.data.msgs.map((item) => item.id))
      const next = [
        ...this.data.msgs,
        ...normalized.filter((item) => !existing.has(item.id))
      ]
      this.setData({ msgs: next }, () => this.scrollBottom())
    } catch (err) {
      if (!silent) wx.showToast({ title: err.detail || '消息加载失败', icon: 'none' })
    }
  },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  async send() {
    const text = this.data.input.trim()
    if (!text || this.data.sending) return
    if (!this.saved) {
      wx.showToast({ title: '当前会话不能发送消息', icon: 'none' })
      return
    }
    this.setData({ sending: true })
    try {
      const message = await sendCustomerOrderMessage(this.saved, text)
      const normalized = normalizeMessage(message)
      this.lastMessageId = Math.max(this.lastMessageId, message.id)
      this.setData({
        msgs: [...this.data.msgs, normalized],
        input: ''
      }, () => this.scrollBottom())
    } catch (err) {
      wx.showToast({ title: err.detail || '消息发送失败', icon: 'none' })
    } finally {
      this.setData({ sending: false })
    }
  },

  goSetting() {
    wx.navigateTo({ url: '/pages/message/setting' })
  },

  goHistory() {
    wx.navigateTo({ url: `/pages/message/history?id=${this.chatId}` })
  },

  goCompanion() {
    wx.navigateTo({ url: `/pages/message/companion?id=${this.orderId || ''}` })
  }
})
