Page({
  data: {
    name: '张陪护师',
    input: '',
    msgs: [
      { id: 1, from: 'me', text: '您好，我预约了 13:00 的陪诊', time: '10:20' },
      { id: 2, from: 'other', text: '您好，我已收到预约，13:00 准时到。', time: '10:23' },
      { id: 3, from: 'other', text: '请问您今天方便吗？', time: '10:24' }
    ]
  },
  onInput(e) { this.setData({ input: e.detail.value }) },
  send() {
    if (!this.data.input) return
    const list = [...this.data.msgs, { id: Date.now(), from: 'me', text: this.data.input, time: '10:30' }]
    this.setData({ msgs: list, input: '' })
  },
  goSetting() { wx.navigateTo({ url: '/pages/message/setting' }) },
  goHistory() { wx.navigateTo({ url: '/pages/message/history' }) },
  goCompanion() { wx.navigateTo({ url: '/pages/message/companion' }) }
})
