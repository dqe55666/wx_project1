const { request } = require('../../utils/api')

Page({
  data: {
    statusBarHeight: 20,
    menuSafeRight: 0,
    cityName: '定位中',
    keyword: '',
    hospitals: [],
    hospitalLoading: false,
    locating: false,
    // 本期优秀陪护师（6 位）——展示顺序 = 数组顺序，调整排序只需改这里的排列
    nurses: [
      { id: 1, name: '肖雯遥', avatar: '/assets/images/nurses/肖雯遥.jpg' },
      { id: 2, name: '王一茜', avatar: '/assets/images/nurses/王一茜.jpg' },
      { id: 3, name: '彭彦博', avatar: '/assets/images/nurses/彭彦博.jpg' },
      { id: 4, name: '方嘉倩', avatar: '/assets/images/nurses/方嘉倩.jpg' },
      { id: 5, name: '胡冰冰', avatar: '/assets/images/nurses/胡冰冰.jpg' },
      { id: 6, name: '谢远杰', avatar: '/assets/images/nurses/谢远杰.jpg' }
    ]
  },

  onLoad() {
    this.setupNavMetrics()
    this.loadHospitals()
    this.refreshLocation()
  },

  // 计算状态栏高度与右上角胶囊避让宽度（自定义导航栏）
  setupNavMetrics() {
    const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync()
    const rpx2px = (info.windowWidth || 375) / 750
    let menuSafeRight = 0
    try {
      const menu = wx.getMenuButtonBoundingClientRect()
      if (menu && menu.left) {
        // 顶部栏所在容器本身已有 30rpx 右内边距，这里扣掉它，避免避让空间叠加
        // 导致搜索框被压得放不下文案
        menuSafeRight = Math.round(info.windowWidth - menu.left + 6 - 30 * rpx2px)
      }
    } catch (err) {
      menuSafeRight = 96
    }
    this.setData({
      statusBarHeight: info.statusBarHeight || 20,
      menuSafeRight
    })
  },

  onCityTap() {
    this.refreshLocation()
  },

  refreshLocation() {
    if (this.data.locating) return
    this.setData({ locating: true })
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        const userLocation = { latitude: res.latitude, longitude: res.longitude }
        this.setData({ userLocation })
        this.loadHospitals(userLocation)
        this.reverseGeocode(userLocation)
      },
      fail: () => {
        this.setData({ locating: false, cityName: '定位失败' })
        wx.showToast({ title: '未授权定位', icon: 'none' })
      }
    })
  },

  async loadHospitals(location) {
    this.setData({ hospitalLoading: true })
    try {
      const query = location ? `?lat=${location.latitude}&lng=${location.longitude}` : ''
      const hospitals = await request(`/api/hospitals${query}`)
      this.setData({
        hospitals: hospitals.map((item) => ({
          ...item,
          displayDistance: this.formatDistance(item.distance_km)
        }))
      })
    } catch (err) {
      // 静默失败，页面保留空态
    } finally {
      this.setData({ hospitalLoading: false })
    }
  },

  async reverseGeocode(location) {
    try {
      const result = await request(`/api/location/regeo?lat=${location.latitude}&lng=${location.longitude}`)
      const address = result.formatted_address || ''
      this.setData({
        cityName: this.extractCity(address) || '当前位置',
        locating: false
      })
    } catch (err) {
      this.setData({ cityName: '当前位置', locating: false })
    }
  },

  extractCity(address) {
    if (!address) return ''
    const match = address.match(/(.{2,5}?(?:市|州|地区|盟))/)
    if (match) return match[1]
    return address.slice(0, 4)
  },

  formatDistance(distance) {
    if (distance === null || distance === undefined) return ''
    return `${distance}km`
  },

  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearchTap() {    const keyword = (this.data.keyword || '').trim()
    if (!keyword) {
      wx.showToast({ title: '请输入搜索内容', icon: 'none' })
      return
    }
    wx.showToast({ title: '搜索功能开发中', icon: 'none' })
  },

  goCreateVisit() {    wx.navigateTo({ url: '/pages/visit/create' })
  },

  goPackage() {    wx.showToast({ title: '套餐功能开发中', icon: 'none' })
  },

  goMall() {    wx.navigateTo({ url: '/pages/mall/index' })
  },

  goBottle() {    wx.navigateTo({ url: '/pages/bottle/bottle' })
  },

  goNurses() {    wx.showToast({ title: '陪护师列表开发中', icon: 'none' })
  },

  openOrdersPage() {    wx.navigateTo({ url: '/pages/orders/orders' })
  },

  onHospitalTap() {    wx.navigateTo({ url: '/pages/visit/create' })
  }
})
