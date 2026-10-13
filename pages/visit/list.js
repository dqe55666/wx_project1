const { fetchCustomerOrders, request } = require('../../utils/api')

Page({
  data: {
    city: '定位中',
    currentTab: 0,
    tabs: ['进行中', '已完成'],
    list: [],
    showList: [],
    loading: false
  },

  onLoad() {
    this.refreshCity()
  },

  onShow() {
    this.loadOrders()
  },

  async loadOrders() {
    this.setData({ loading: true })
    try {
      const list = await fetchCustomerOrders()
      this.setData({ list })
      this.applyFilter()
    } catch (err) {
      wx.showToast({ title: '陪诊记录加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 按当前 tab 预先分好数组：既免掉 wxml 里 wx:if 全量遍历，也让空态判断准确
  applyFilter() {
    const tab = this.data.currentTab
    const showList = (this.data.list || []).filter((item) =>
      tab === 0 ? item.visitStatus === 'ongoing' : item.visitStatus === 'done'
    )
    this.setData({ showList })
  },

  onPullDownRefresh() {
    this.refreshCity()
    this.loadOrders().finally(() => wx.stopPullDownRefresh())
  },

  onTabChange(e) {
    const currentTab = Number(e.currentTarget.dataset.index) || 0
    this.setData({ currentTab }, () => this.applyFilter())
  },

  pickCity() {    this.refreshCity(true)
  },

  refreshCity(showLoading = false) {
    if (showLoading) wx.showLoading({ title: '正在定位' })
    wx.getLocation({
      type: 'gcj02',
      success: async (res) => {
        try {
          const result = await request(`/api/location/regeo?lat=${res.latitude}&lng=${res.longitude}`)
          const city = result.city || result.province || '当前位置'
          this.setData({ city })
        } catch (err) {
          this.setData({ city: '定位地址获取失败' })
        } finally {
          if (showLoading) wx.hideLoading()
        }
      },
      fail: () => {
        this.setData({ city: '未授权定位' })
        if (showLoading) wx.hideLoading()
      }
    })
  },

  goSearch() {    wx.showToast({ title: '请在我的订单中查看全部预约', icon: 'none' })
  },

  goDetail(e) {    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/visit/detail?id=' + id })
  },

  goCreate() {    wx.navigateTo({ url: '/pages/visit/create' })
  },

  goAccompany() {    wx.navigateTo({ url: '/pages/visit/accompany' })
  },

  goReserveType() {    wx.navigateTo({ url: '/pages/visit/reserve-type' })
  },

  goOrders() {    wx.navigateTo({ url: '/pages/mine/orders' })
  },

  finishVisit(e) {    e.stopPropagation && e.stopPropagation()
    wx.showToast({ title: '服务结束由后台或员工端确认', icon: 'none' })
  },

  overtime(e) {    e.stopPropagation && e.stopPropagation()
    wx.navigateTo({ url: '/pages/visit/overtime?id=' + e.currentTarget.dataset.id })
  },

  evaluate(e) {    e.stopPropagation && e.stopPropagation()
    wx.navigateTo({ url: '/pages/visit/evaluate?id=' + e.currentTarget.dataset.id })
  }
})
