Page({
  data: {
    mute: false,
    top: false
  },
  toggleMute() { this.setData({ mute: !this.data.mute }) },
  toggleTop() { this.setData({ top: !this.data.top }) },
  clear() { wx.showModal({ title: '提示', content: '确认清空聊天记录？', success: r => r.confirm && wx.showToast({ title: '已清空', icon: 'success' }) }) },
  report() { wx.showToast({ title: '已提交（壳子）', icon: 'none' }) }
})
