// pages/visit/list.js
Page({
  data: {
    city: '张家界市',
    currentTab: 0, // 0 进行中  1 已完成
    tabs: ['进行中', '已完成'],
    list: [
      {
        id: 'V001',
        orderNo: 'PZ580579578903',
        type: 'vip',
        typeName: 'VIP陪诊',
        hospital: '张家界市人民医院',
        address: '张家界市永定区古庸路192号',
        dept: '消化内科',
        time: '2023-12-01  13:00-16:30',
        doctor: '张三',
        phone: '18812345678',
        status: 'ongoing'
      },
      {
        id: 'V002',
        orderNo: 'PZ580579578903',
        type: 'normal',
        typeName: '普通陪诊',
        hospital: '张家界市人民医院',
        address: '张家界市永定区古庸路192号',
        dept: '消化内科',
        time: '2023-12-01  13:00-16:30',
        doctor: '张三',
        phone: '18812345678',
        status: 'done'
      }
    ]
  },

  onPullDownRefresh() {
    setTimeout(() => wx.stopPullDownRefresh(), 600)
  },

  switchTab(e) {
    this.setData({ currentTab: e.currentTarget.dataset.index })
  },

  pickCity() {
    wx.showToast({ title: '选择城市（壳子）', icon: 'none' })
  },

  goSearch() {
    wx.showToast({ title: '搜索（壳子）', icon: 'none' })
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/visit/detail?id=' + id })
  },

  goCreate() {
    wx.navigateTo({ url: '/pages/visit/create' })
  },

  goAccompany() {
    wx.navigateTo({ url: '/pages/visit/accompany' })
  },

  goReserveType() {
    wx.navigateTo({ url: '/pages/visit/reserve-type' })
  },

  goOrders() {
    wx.navigateTo({ url: '/pages/mine/orders' })
  },

  finishVisit(e) {
    e.stopPropagation && e.stopPropagation()
    wx.navigateTo({ url: '/pages/visit/finish' })
  },

  overtime(e) {
    e.stopPropagation && e.stopPropagation()
    wx.navigateTo({ url: '/pages/visit/overtime' })
  },

  evaluate(e) {
    e.stopPropagation && e.stopPropagation()
    wx.navigateTo({ url: '/pages/visit/evaluate' })
  }
})
