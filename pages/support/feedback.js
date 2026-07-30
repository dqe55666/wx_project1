const { createSupportTicket, saveSupportTicket } = require('../../utils/api')

Page({
  data: { subject: '', content: '', submitting: false },
  onSubjectInput(e) { this.setData({ subject: e.detail.value }) },
  onContentInput(e) { this.setData({ content: e.detail.value }) },
  async submit() {
    const content = this.data.content.trim()
    if (!content) {
      wx.showToast({ title: '请填写反馈内容', icon: 'none' })
      return
    }
    const user = getApp().globalData.userInfo || wx.getStorageSync('userInfo') || {}
    this.setData({ submitting: true })
    try {
      const ticket = await createSupportTicket({
        category: 'feedback',
        subject: this.data.subject.trim() || null,
        content,
        customer_name: user.nickName || '小陪用户',
        customer_avatar: user.avatarUrl || null
      })
      saveSupportTicket(ticket)
      wx.showModal({
        title: '反馈已提交',
        content: '客服处理结果会通过此反馈会话回复。',
        showCancel: false,
        success: () => wx.redirectTo({ url: `/pages/support/chat?ticketId=${ticket.id}` })
      })
    } catch (err) {
      wx.showToast({ title: err.detail || '提交失败，请稍后重试', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  }
})
