Page({
  data: {
    dates: ['今天 11-28', '明天 11-29', '周三 11-30', '周四 12-01', '周五 12-02', '周六 12-03', '周日 12-04'],
    times: ['09:00-10:00', '10:00-11:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'],
    dateIdx: 0,
    timeIdx: 2
  },
  pickDate(e) { this.setData({ dateIdx: e.currentTarget.dataset.i }) },
  pickTime(e) { this.setData({ timeIdx: e.currentTarget.dataset.i }) },
  confirm() {
    const text = this.data.dates[this.data.dateIdx] + ' ' + this.data.times[this.data.timeIdx]
    wx.showLoading({ title: '提交中...' })
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({ title: '预约成功', icon: 'success' })
      setTimeout(() => {
        // 下单完成：跳到陪诊中 Tab
        wx.switchTab({
          url: '/pages/visit/list',
          fail: () => {
            wx.reLaunch({ url: '/pages/visit/list' })
          }
        })
      }, 600)
    }, 400)
  }
})
