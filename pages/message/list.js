Page({
  data: {
    list: [
      { id: 'm1', avatar: '👩‍⚕️', name: '张陪护师', desc: '已为您预约好 13:00 准时到达', time: '10:23', unread: 2 },
      { id: 'm2', avatar: '🧑‍⚕️', name: '李陪护师', desc: '请问您今天方便吗？', time: '昨天', unread: 0 },
      { id: 'm3', avatar: '🏥', name: '系统通知', desc: '您的订单 PZ58057 已完成', time: '12-01', unread: 1 },
      { id: 'm4', avatar: '💬', name: '客服小陪', desc: '您好，请问有什么可以帮您？', time: '11-30', unread: 0 }
    ]
  },

  goChat(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/message/chat?id=' + id })
  },

  goNotice() {
    // 通知：直接打开系统通知会话
    wx.navigateTo({ url: '/pages/message/chat?id=system' })
  },

  goCalendar() {
    // 日程：跳到陪诊中查看时间安排
    wx.switchTab({ url: '/pages/visit/list', fail: () => wx.navigateTo({ url: '/pages/visit/list' }) })
  },

  goMall() {
    wx.switchTab({ url: '/pages/mall/index', fail: () => wx.navigateTo({ url: '/pages/mall/index' }) })
  },

  goOrders() {
    wx.navigateTo({ url: '/pages/mine/orders' })
  }
})
