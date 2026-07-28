Page({
  data: {
    tabs: ['全部', '待支付', '进行中', '待评价'],
    current: 0,
    list: [
      { id: 1, no: 'PZ580579578903', type: 'VIP陪诊', hospital: '张家界市人民医院', status: '进行中', statusIdx: 2 },
      { id: 2, no: 'PZ580579578901', type: '普通陪诊', hospital: '张家界市人民医院', status: '待支付', statusIdx: 1 },
      { id: 3, no: 'PZ580579578900', type: '普通陪诊', hospital: '张家界市中医院', status: '待评价', statusIdx: 3 }
    ]
  },
  switchTab(e) { this.setData({ current: e.currentTarget.dataset.i }) },
  goDetail(e) { wx.navigateTo({ url: '/pages/visit/detail?id=' + e.currentTarget.dataset.id }) }
})
