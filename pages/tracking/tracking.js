const app = getApp()

const REFRESH_INTERVAL = 15000

Page({
  data: {
    orderNo: '',
    staffName: '陪护人员位置',
    customerLocationText: '正在获取当前位置',
    staffLocationText: '等待陪护人员开启位置共享',
    updateText: '页面停留期间每 15 秒自动更新',
    refreshing: false,
    mapLatitude: 31.2304,
    mapLongitude: 121.4737,
    mapScale: 14,
    markers: []
  },

  onLoad(options) {
    this.orderId = Number(options.id)
    this.token = options.token || ''
    if (!this.orderId || !this.token) {
      wx.showToast({ title: '订单信息无效', icon: 'none' })
      wx.navigateBack()
      return
    }
    this.refreshLocations()
  },

  onShow() {
    this.startAutoRefresh()
  },

  onHide() {
    this.stopAutoRefresh()
  },

  onUnload() {
    this.stopAutoRefresh()
  },

  request(path, options = {}) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBaseUrl}${path}`,
        method: options.method || 'GET',
        data: options.data,
        header: { 'content-type': 'application/json' },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
            return
          }
          reject(res.data || {})
        },
        fail: reject
      })
    })
  },

  getCurrentLocation() {
    return new Promise((resolve) => {
      wx.getLocation({
        type: 'gcj02',
        success: (res) => resolve({ latitude: res.latitude, longitude: res.longitude }),
        fail: () => resolve(null)
      })
    })
  },

  async refreshLocations() {
    if (this.data.refreshing) return
    this.setData({ refreshing: true })
    try {
      const currentLocation = await this.getCurrentLocation()
      if (currentLocation) this.applyCurrentLocation(currentLocation)
      if (currentLocation) {
        try {
          await this.request(
            `/api/customer/orders/${this.orderId}/location?token=${encodeURIComponent(this.token)}`,
            { method: 'POST', data: currentLocation }
          )
        } catch (err) {
          console.warn('[location] customer location upload failed', err)
        }
      }
      const orderLocation = await this.request(`/api/customer/orders/${this.orderId}/location?token=${encodeURIComponent(this.token)}`)
      this.applyLocations(orderLocation, currentLocation || orderLocation.customer_location)
    } catch (err) {
      wx.showToast({ title: err.detail || '位置更新失败', icon: 'none' })
    } finally {
      this.setData({ refreshing: false })
    }
  },

  applyCurrentLocation(location) {
    this.setData({
      customerLocationText: '正在实时定位',
      mapLatitude: location.latitude,
      mapLongitude: location.longitude,
      mapScale: 15,
      markers: [{
        id: 1,
        latitude: location.latitude,
        longitude: location.longitude,
        width: 34,
        height: 34,
        callout: { content: '我的位置', display: 'ALWAYS', color: '#c2185b', fontSize: 12, borderRadius: 4, padding: 5, bgColor: '#ffffff' }
      }]
    })
  },

  applyLocations(orderLocation, customerLocation) {
    const staffLocation = orderLocation.staff_location
    const markers = []
    if (customerLocation) {
      markers.push({
        id: 1,
        latitude: customerLocation.latitude,
        longitude: customerLocation.longitude,
        width: 34,
        height: 34,
        callout: { content: '我的位置', display: 'ALWAYS', color: '#c2185b', fontSize: 12, borderRadius: 4, padding: 5, bgColor: '#ffffff' }
      })
    }
    if (staffLocation) {
      markers.push({
        id: 2,
        latitude: staffLocation.latitude,
        longitude: staffLocation.longitude,
        width: 34,
        height: 34,
        callout: { content: orderLocation.employee_name || '陪护人员', display: 'ALWAYS', color: '#00796b', fontSize: 12, borderRadius: 4, padding: 5, bgColor: '#ffffff' }
      })
    }
    const center = staffLocation || customerLocation
    this.setData({
      orderNo: orderLocation.order_no,
      staffName: orderLocation.employee_name || '陪护人员位置',
      customerLocationText: customerLocation ? '正在实时定位' : '尚未提交服务地址坐标',
      staffLocationText: staffLocation ? `最近更新：${this.formatTime(staffLocation.updated_at)}` : '等待陪护人员开启位置共享',
      updateText: staffLocation ? '页面停留期间每 15 秒自动更新' : '陪护人员位置将在开启共享后显示',
      markers,
      mapLatitude: center ? center.latitude : this.data.mapLatitude,
      mapLongitude: center ? center.longitude : this.data.mapLongitude,
      mapScale: markers.length > 1 ? 12 : 15
    })
  },

  formatTime(value) {
    if (!value) return '刚刚'
    return value.replace('T', ' ').slice(0, 16)
  },

  startAutoRefresh() {
    this.stopAutoRefresh()
    this.refreshTimer = setInterval(() => this.refreshLocations(), REFRESH_INTERVAL)
  },

  stopAutoRefresh() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
      this.refreshTimer = null
    }
  }
})
