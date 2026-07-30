const app = getApp()
const { saveCustomerOrder } = require('../../utils/api')

Page({
  data: {
    hospitals: [],
    services: [],
    selectedHospitalIndex: 0,
    selectedServiceIndex: 0,
    locationReady: false,
    hospitalLoading: false,
    locating: false,
    submitting: false,
    form: {
      patientName: '',
      patientPhone: '',
      addressDetail: '',
      appointmentDate: '',
      appointmentTime: '09:00',
      note: ''
    },
    currentAddress: '',
    userLocation: null
  },

  onLoad() {
    this.setData({
      'form.appointmentDate': this.formatDate(new Date())
    })
    this.loadServices()
    this.loadHospitals()
    this.refreshLocation()
  },

  request(path, options = {}) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBaseUrl}${path}`,
        method: options.method || 'GET',
        data: options.data,
        header: {
          'content-type': 'application/json'
        },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
            return
          }
          reject(res.data)
        },
        fail: reject
      })
    })
  },

  async loadHospitals(location) {
    this.setData({ hospitalLoading: true })
    try {
      const query = location ? `?lat=${location.latitude}&lng=${location.longitude}` : ''
      console.info('[hospitals] request', query || 'without location')
      const hospitals = await this.request(`/api/hospitals${query}`)
      console.info('[hospitals] response count', hospitals.length)
      if (!hospitals.length && this.data.hospitals.length) {
        wx.showToast({ title: '定位后暂无匹配单位，保留原列表', icon: 'none' })
        return
      }
      this.setData({
        hospitals: hospitals.map((item) => ({
          ...item,
          displayDistance: this.formatDistance(item.distance_km)
        })),
        selectedHospitalIndex: 0
      })
    } catch (err) {
      console.error('[hospitals] failed', err)
      wx.showToast({ title: '医院列表加载失败', icon: 'none' })
    } finally {
      this.setData({ hospitalLoading: false })
    }
  },

  async loadServices() {
    try {
      const services = await this.request('/api/services')
      this.setData({
        services: services.map((item) => ({
          ...item,
          displayPrice: this.formatPrice(item.price_cents)
        }))
      })
    } catch (err) {
      wx.showToast({ title: '服务项目加载失败', icon: 'none' })
    }
  },

  refreshLocation() {
    this.setData({ locating: true })
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        const userLocation = {
          latitude: res.latitude,
          longitude: res.longitude
        }
        this.setData({
          userLocation,
          locationReady: true
        })
        this.loadHospitals(userLocation)
        this.reverseGeocodeLocation(userLocation)
      },
      fail: () => {
        this.setData({
          locationReady: false,
          locating: false
        })
        wx.showToast({ title: '未授权定位，将不显示距离', icon: 'none' })
      }
    })
  },

  async reverseGeocodeLocation(location) {
    try {
      const result = await this.request(`/api/location/regeo?lat=${location.latitude}&lng=${location.longitude}`)
      const currentAddress = result.formatted_address || `${location.latitude},${location.longitude}`
      const updates = {
        currentAddress,
        locating: false
      }
      if (!this.data.form.addressDetail.trim() && result.formatted_address) {
        updates['form.addressDetail'] = result.formatted_address
      }
      this.setData(updates)
    } catch (err) {
      console.error('[location] regeo failed', err)
      this.setData({
        currentAddress: `${location.latitude},${location.longitude}`,
        locating: false
      })
      wx.showToast({ title: '地址解析失败，已获取坐标', icon: 'none' })
    }
  },

  onHospitalChange(e) {
    this.setData({ selectedHospitalIndex: Number(e.detail.value) })
  },

  openOrdersPage() {
    wx.navigateTo({ url: '/pages/orders/orders' })
  },

  onServiceChange(e) {
    this.setData({ selectedServiceIndex: Number(e.detail.value) })
  },

  onFieldInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({
      [`form.${field}`]: e.detail.value
    })
  },

  formatPrice(priceCents) {
    return `¥${(priceCents / 100).toFixed(2)}`
  },

  formatDistance(distance) {
    if (distance === null || distance === undefined) {
      return '距离待定位'
    }
    return `${distance} km`
  },

  formatDate(date) {
    const year = date.getFullYear()
    const month = `${date.getMonth() + 1}`.padStart(2, '0')
    const day = `${date.getDate()}`.padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  validateOrder() {
    const { form, hospitals, services } = this.data
    if (!hospitals.length) return '请选择医院单位'
    if (!services.length) return '请选择服务项目'
    if (!form.patientName.trim()) return '请填写患者姓名'
    if (!/^[0-9+()\- ]{6,30}$/.test(form.patientPhone.trim())) return '请填写正确的联系电话'
    if (!form.addressDetail.trim()) return '请填写服务地址'
    if (!form.appointmentDate || !form.appointmentTime) return '请选择预约时间'
    if (new Date(`${form.appointmentDate}T${form.appointmentTime}:00`).getTime() <= Date.now()) {
      return '预约时间需晚于当前时间'
    }
    return ''
  },

  async submitOrder() {
    const message = this.validateOrder()
    if (message) {
      wx.showToast({ title: message, icon: 'none' })
      return
    }

    const {
      form,
      hospitals,
      services,
      selectedHospitalIndex,
      selectedServiceIndex,
      userLocation
    } = this.data
    const hospital = hospitals[selectedHospitalIndex]
    const service = services[selectedServiceIndex]
    const payload = {
      hospital_id: hospital.id,
      service_item_id: service.id,
      patient_name: form.patientName.trim(),
      patient_phone: form.patientPhone.trim(),
      appointment_time: `${form.appointmentDate}T${form.appointmentTime}:00+08:00`,
      address_detail: form.addressDetail.trim(),
      latitude: userLocation ? userLocation.latitude : null,
      longitude: userLocation ? userLocation.longitude : null,
      note: form.note.trim() || null
    }

    this.setData({ submitting: true })
    try {
      const order = await this.request('/api/orders', {
        method: 'POST',
        data: payload
      })
      saveCustomerOrder(order)
      wx.showModal({
        title: '预约已提交',
        content: `订单号：${order.order_no}`,
        showCancel: false,
        success: () => wx.navigateTo({ url: '/pages/orders/orders' })
      })
      this.setData({
        'form.patientName': '',
        'form.patientPhone': '',
        'form.addressDetail': '',
        'form.note': ''
      })
    } catch (err) {
      wx.showToast({ title: err.detail || '提交失败，请稍后重试', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  }
})
