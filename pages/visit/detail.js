const { fetchCustomerOrder, getSavedOrder, request } = require('../../utils/api')

const LOCATION_REFRESH_INTERVAL = 15000

Page({
  data: {
    loading: false,
    order: {
      no: '',
      typeName: '陪诊服务',
      hospital: '',
      address: '',
      dept: '',
      time: '',
      doctor: '待接单',
      phone: '',
      displayPrice: '',
      statusText: ''
    },
    tracking: {
      visible: false,
      staffName: '陪诊师位置',
      staffLocationText: '等待陪诊师开启位置共享',
      customerLocationText: '正在获取位置',
      mapLatitude: 31.2304,
      mapLongitude: 121.4737,
      mapScale: 14,
      markers: []
    },
    respondingEarlyFinish: false
  },

  onLoad(options) {
    this.orderId = Number(options.id)
    this.loadOrder()
  },

  onShow() {
    this.startLocationRefresh()
  },

  onHide() {
    this.stopLocationRefresh()
  },

  onUnload() {
    this.stopLocationRefresh()
  },

  async loadOrder() {
    const saved = getSavedOrder(this.orderId)
    if (!saved) {
      wx.showToast({ title: '订单凭据已失效', icon: 'none' })
      return
    }
    this.setData({ loading: true })
    try {
      const order = await fetchCustomerOrder(saved)
      this.setData({ order })
      if (this.isOrderActive(order)) {
        this.refreshLocations()
      } else {
        this.setData({ 'tracking.visible': false })
      }
    } catch (err) {
      wx.showToast({ title: err.detail || '订单详情加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  callPhone() {
    if (!this.data.order.phone) {
      wx.showToast({ title: '待接单后显示电话', icon: 'none' })
      return
    }
    wx.makePhoneCall({ phoneNumber: this.data.order.phone }).catch(() => {})
  },

  chat() {
    wx.navigateTo({ url: `/pages/message/chat?id=order-${this.orderId || ''}` })
  },

  isOrderActive(order) {
    return order && (order.status === 'accepted' || order.status === 'in_progress')
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
    const saved = getSavedOrder(this.orderId)
    if (!saved || !this.isOrderActive(this.data.order) || this.locationRefreshing) return
    this.locationRefreshing = true
    try {
      const currentLocation = await this.getCurrentLocation()
      if (currentLocation) {
        try {
          await request(`/api/customer/orders/${this.orderId}/location?token=${encodeURIComponent(saved.token)}`, {
            method: 'POST',
            data: currentLocation
          })
        } catch (err) {
          console.warn('[tracking] customer location upload failed', err)
        }
      }
      const location = await request(`/api/customer/orders/${this.orderId}/location?token=${encodeURIComponent(saved.token)}`)
      this.applyLocations(location, currentLocation || location.customer_location)
    } catch (err) {
      console.warn('[tracking] location refresh failed', err)
    } finally {
      this.locationRefreshing = false
    }
  },

  applyLocations(location, customerLocation) {
    const staffLocation = location.staff_location
    const markers = []
    if (customerLocation) {
      markers.push({
        id: 1,
        latitude: customerLocation.latitude,
        longitude: customerLocation.longitude,
        width: 30,
        height: 30,
        callout: { content: '我的位置', display: 'ALWAYS', color: '#c2185b', fontSize: 11, borderRadius: 4, padding: 5, bgColor: '#ffffff' }
      })
    }
    if (staffLocation) {
      markers.push({
        id: 2,
        latitude: staffLocation.latitude,
        longitude: staffLocation.longitude,
        width: 30,
        height: 30,
        callout: { content: location.employee_name || '陪诊师', display: 'ALWAYS', color: '#00796b', fontSize: 11, borderRadius: 4, padding: 5, bgColor: '#ffffff' }
      })
    }
    const center = staffLocation || customerLocation
    this.setData({
      'tracking.visible': true,
      'tracking.staffName': location.employee_name || '陪诊师位置',
      'tracking.staffLocationText': staffLocation ? `最近更新：${this.formatTime(staffLocation.updated_at)}` : '等待陪诊师开启位置共享',
      'tracking.customerLocationText': customerLocation ? '正在实时定位' : '尚未获取当前位置',
      'tracking.markers': markers,
      'tracking.mapLatitude': center ? center.latitude : this.data.tracking.mapLatitude,
      'tracking.mapLongitude': center ? center.longitude : this.data.tracking.mapLongitude,
      'tracking.mapScale': markers.length > 1 ? 12 : 15
    })
  },

  formatTime(value) {
    return value ? value.replace('T', ' ').slice(0, 16) : '刚刚'
  },

  startLocationRefresh() {
    this.stopLocationRefresh()
    this.locationTimer = setInterval(() => this.refreshLocations(), LOCATION_REFRESH_INTERVAL)
  },

  stopLocationRefresh() {
    if (this.locationTimer) {
      clearInterval(this.locationTimer)
      this.locationTimer = null
    }
  },

  async respondEarlyFinish(e) {
    const saved = getSavedOrder(this.orderId)
    if (!saved || this.data.respondingEarlyFinish) return
    const approved = Boolean(e.currentTarget.dataset.approved)
    this.setData({ respondingEarlyFinish: true })
    try {
      await request(`/api/customer/orders/${this.orderId}/early-finish-response?token=${encodeURIComponent(saved.token)}`, {
        method: 'POST',
        data: { approved }
      })
      wx.showToast({ title: approved ? '已同意提前结束' : '已通知员工继续服务', icon: 'none' })
      this.loadOrder()
    } catch (err) {
      wx.showToast({ title: err.detail || '提交协商结果失败', icon: 'none' })
    } finally {
      this.setData({ respondingEarlyFinish: false })
    }
  }
})
