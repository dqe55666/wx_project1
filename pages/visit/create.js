Page({
  data: {
    hospital: '张家界市人民医院',
    service: '基础陪诊',
    name: '',
    phone: '',
    date: '',
    time: '09:00'
  },
  goInfo() { wx.navigateTo({ url: '/pages/visit/info' }) },
  goAccompany() { wx.navigateTo({ url: '/pages/visit/accompany' }) },
  goReserveTime() { wx.navigateTo({ url: '/pages/visit/reserve-time' }) },
  goReserveType() { wx.navigateTo({ url: '/pages/visit/reserve-type' }) },
  // 下单完整流程：先选类型 → 再选陪诊师 → 再选时间 → 回到陪诊中
  submit() {
    wx.navigateTo({ url: '/pages/visit/reserve-type' })
  }
})
