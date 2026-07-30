const { request, saveCustomerOrder } = require('../../utils/api')

Page({
  data: {
    hospitals: [],
    services: [],
    serviceTypes: ['门诊陪诊', '检查陪同', '取药取报告'],
    selectedHospitalIndex: 0,
    selectedServiceIndex: 0,
    selectedServiceTypeIndex: 0,
    hospitalLoading: false,
    locating: false,
    submitting: false,
    currentAddress: '',
    userLocation: null,
    form: {
      patientName: '',
      patientPhone: '',
      addressDetail: '',
      appointmentDate: '',
      appointmentTime: '09:00',
      note: ''
    }
  },

  onLoad() {
    const appointmentDate = new Date()
    if (appointmentDate.getHours() >= 9) appointmentDate.setDate(appointmentDate.getDate() + 1)
    this.setData({ 'form.appointmentDate': this.formatDate(appointmentDate) })
    this.loadServices()
    this.loadHospitals()
    this.refreshLocation()
  },

  async loadHospitals(location) {
    this.setData({ hospitalLoading: true })
    try {
      const query = location ? `?lat=${location.latitude}&lng=${location.longitude}` : ''
      const hospitals = await request(`/api/hospitals${query}`)
      this.setData({ hospitals, selectedHospitalIndex: 0 })
    } catch (err) {
      wx.showToast({ title: err.detail || '医院列表加载失败', icon: 'none' })
    } finally {
      this.setData({ hospitalLoading: false })
    }
  },

  async loadServices() {
    try {
      const services = await request('/api/services')
      this.setData({ services, selectedServiceIndex: 0 })
    } catch (err) {
      wx.showToast({ title: err.detail || '服务项目加载失败', icon: 'none' })
    }
  },

  refreshLocation() {
    this.setData({ locating: true })
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        const userLocation = { latitude: res.latitude, longitude: res.longitude }
        this.setData({ userLocation })
        this.loadHospitals(userLocation)
        this.reverseGeocodeLocation(userLocation)
      },
      fail: () => {
        this.setData({ locating: false })
        wx.showToast({ title: '未授权定位，请手动填写服务地址', icon: 'none' })
      }
    })
  },

  async reverseGeocodeLocation(location) {
    try {
      const result = await request(`/api/location/regeo?lat=${location.latitude}&lng=${location.longitude}`)
      const address = result.formatted_address || `${location.latitude},${location.longitude}`
      const updates = { currentAddress: address, locating: false }
      if (!this.data.form.addressDetail.trim()) updates['form.addressDetail'] = address
      this.setData(updates)
    } catch (err) {
      const address = `${location.latitude},${location.longitude}`
      const updates = {
        currentAddress: address,
        locating: false
      }
      if (!this.data.form.addressDetail.trim()) updates['form.addressDetail'] = address
      this.setData(updates)
    }
  },

  onHospitalChange(e) {
    this.setData({ selectedHospitalIndex: Number(e.detail.value) })
  },

  onServiceChange(e) {
    this.setData({ selectedServiceIndex: Number(e.detail.value) })
  },

  onServiceTypeChange(e) {
    this.setData({ selectedServiceTypeIndex: Number(e.detail.value) })
  },

  onFieldInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },

  formatDate(date) {
    const year = date.getFullYear()
    const month = `${date.getMonth() + 1}`.padStart(2, '0')
    const day = `${date.getDate()}`.padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  validateOrder() {
    const { form, hospitals, services } = this.data
    if (!hospitals.length) return '请选择就诊医院'
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

  async submit() {
    const message = this.validateOrder()
    if (message) {
      wx.showToast({ title: message, icon: 'none' })
      return
    }
    const { form, hospitals, services, serviceTypes, selectedHospitalIndex, selectedServiceIndex, selectedServiceTypeIndex, userLocation } = this.data
    const detailNote = [
      `服务类型：${serviceTypes[selectedServiceTypeIndex]}`,
      form.note.trim()
    ].filter(Boolean).join('\n')
    this.setData({ submitting: true })
    try {
      const order = await request('/api/orders', {
        method: 'POST',
        data: {
          hospital_id: hospitals[selectedHospitalIndex].id,
          service_item_id: services[selectedServiceIndex].id,
          patient_name: form.patientName.trim(),
          patient_phone: form.patientPhone.trim(),
          appointment_time: `${form.appointmentDate}T${form.appointmentTime}:00+08:00`,
          address_detail: form.addressDetail.trim(),
          latitude: userLocation ? userLocation.latitude : null,
          longitude: userLocation ? userLocation.longitude : null,
          note: detailNote || null
        }
      })
      saveCustomerOrder(order)
      wx.showModal({
        title: '预约已提交',
        content: `订单号：${order.order_no}`,
        showCancel: false,
        success: () => wx.switchTab({ url: '/pages/visit/list' })
      })
    } catch (err) {
      wx.showToast({ title: err.detail || '提交失败，请稍后重试', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  }
})
