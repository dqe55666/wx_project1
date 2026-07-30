const {
  createSupportTicket,
  fetchSupportMessages,
  fetchSupportTicket,
  getLatestSupportTicket,
  getSavedSupportTicket,
  saveSupportTicket,
  sendSupportMessage,
  formatDateTime
} = require('../../utils/api')

function profile() {
  const user = getApp().globalData.userInfo || wx.getStorageSync('userInfo') || {}
  return {
    customer_name: user.nickName || user.name || '小陪用户',
    customer_avatar: user.avatarUrl || user.avatar || null
  }
}

Page({
  data: {
    ticket: null,
    messages: [],
    input: '',
    sending: false,
    loading: false,
    scrollIntoView: 'bottom',
    resolved: false
  },

  onLoad(options) {
    this.saved = options.ticketId ? getSavedSupportTicket(options.ticketId) : getLatestSupportTicket('support')
    this.lastMessageId = 0
    if (this.saved) this.loadTicket()
  },

  onUnload() {
    if (this.pollTimer) clearInterval(this.pollTimer)
  },

  async loadTicket() {
    this.setData({ loading: true })
    try {
      const ticket = await fetchSupportTicket(this.saved)
      this.setData({ ticket, resolved: ticket.status === 'resolved' })
      await this.loadMessages()
      this.startPolling()
    } catch (err) {
      this.saved = null
      this.setData({ ticket: null, messages: [] })
    } finally {
      this.setData({ loading: false })
    }
  },

  startPolling() {
    if (this.pollTimer) clearInterval(this.pollTimer)
    this.pollTimer = setInterval(() => this.loadMessages(true), 5000)
  },

  async loadMessages(silent = false) {
    if (!this.saved) return
    try {
      const messages = await fetchSupportMessages(this.saved, this.lastMessageId)
      if (!messages.length) return
      this.lastMessageId = Math.max(this.lastMessageId, ...messages.map((item) => item.id))
      const existing = new Set(this.data.messages.map((item) => item.id))
      this.setData({
        messages: [...this.data.messages, ...messages.filter((item) => !existing.has(item.id)).map((item) => ({
          ...item,
          from: item.sender_type === 'customer' ? 'me' : 'other',
          displayTime: formatDateTime(item.created_at)
        }))]
      }, () => this.scrollBottom())
    } catch (err) {
      if (!silent) wx.showToast({ title: err.detail || '消息加载失败', icon: 'none' })
    }
  },

  scrollBottom() {
    this.setData({ scrollIntoView: '' }, () => this.setData({ scrollIntoView: 'bottom' }))
  },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  async send() {
    const content = this.data.input.trim()
    if (!content || this.data.sending) return
    this.setData({ sending: true })
    try {
      if (!this.saved || this.data.resolved) {
        const ticket = await createSupportTicket({ category: 'support', content, ...profile() })
        saveSupportTicket(ticket)
        this.saved = { id: ticket.id, token: ticket.access_token, category: ticket.category }
        this.lastMessageId = 0
        this.setData({ ticket, messages: [], resolved: false, input: '' })
        await this.loadMessages()
        this.startPolling()
      } else {
        const message = await sendSupportMessage(this.saved, content)
        this.lastMessageId = Math.max(this.lastMessageId, message.id)
        this.setData({
          input: '',
          messages: [...this.data.messages, { ...message, from: 'me', displayTime: formatDateTime(message.created_at) }]
        }, () => this.scrollBottom())
      }
    } catch (err) {
      wx.showToast({ title: err.detail || '发送失败，请稍后重试', icon: 'none' })
    } finally {
      this.setData({ sending: false })
    }
  }
})
