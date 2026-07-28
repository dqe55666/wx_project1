Page({
  data: {
    services: [
      { id: 1, name: '基础陪诊', desc: '挂号 / 取药 / 问诊引导', price: 198, unit: '次' },
      { id: 2, name: '半日陪诊', desc: '陪诊师陪同 4 小时', price: 398, unit: '半日' },
      { id: 3, name: '全日陪诊', desc: '陪诊师陪同 8 小时', price: 698, unit: '全日' },
      { id: 4, name: 'VIP 陪诊', desc: '1对1 专属陪诊师 + 接送', price: 1280, unit: '次' }
    ]
  },
  select(e) {
    const name = e.currentTarget.dataset.name
    wx.showToast({ title: '已选 ' + name, icon: 'none' })
    setTimeout(() => {
      // 选完陪诊师继续选时间
      wx.redirectTo({ url: '/pages/visit/reserve-time' })
    }, 400)
  }
})
