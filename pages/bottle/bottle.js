Page({
  data: {
    message: '',
    bottleText: '今天辛苦了。慢慢来，也算是在往前走。',
    samples: [
      '愿你今天被认真照顾，也能好好照顾自己。',
      '把紧绷的心放松一点，很多事可以一步一步来。',
      '需要帮忙时开口，不是麻烦别人，是让爱有地方落下。'
    ]
  },

  onMessageInput(e) {
    this.setData({ message: e.detail.value })
  },

  sendBottle() {
    if (!this.data.message.trim()) {
      wx.showToast({ title: '先写一点内容吧', icon: 'none' })
      return
    }
    wx.showToast({ title: '漂瓶已放出', icon: 'success' })
    this.setData({ message: '' })
  },

  pickBottle() {
    const { samples } = this.data
    const index = Math.floor(Math.random() * samples.length)
    this.setData({ bottleText: samples[index] })
  }
})
