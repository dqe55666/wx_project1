const app = getApp()

Page({
  data: {
    employees: [],
    selectedEmployeeIndex: 0,
    selectedEmployeeId: null,
    activeTab: 'pending',
    orders: [],
    loading: false,
    acceptingId: null
  },

  onLoad() {
    this.loadEmployees()
  },

  onShow() {
    if (this.data.selectedEmployeeId) this.loadOrders()
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

  async loadEmployees() {
    try {
      const employees = await this.request('/api/employees')
      const savedId = wx.getStorageSync('employeeId')
      const index = Math.max(0, employees.findIndex((item) => item.id === savedId))
      const selected = employees[index]
      this.setData({
        employees,
        selectedEmployeeIndex: index,
        selectedEmployeeId: selected ? selected.id : null
      })
      if (selected) this.loadOrders()
    } catch (err) {
      wx.showToast({ title: '员工列表加载失败', icon: 'none' })
    }
  },

  async loadOrders() {
    const { selectedEmployeeId, activeTab } = this.data
    if (!selectedEmployeeId) return
    this.setData({ loading: true })
    try {
      const orders = await this.request(
        `/api/employee/orders?employee_id=${selectedEmployeeId}&status=${activeTab}`
      )
      this.setData({ orders: orders.map((item) => ({
        ...item,
        appointmentDisplay: item.appointment_time.replace('T', ' ').slice(0, 16),
        statusText: item.status === 'pending' ? '待接单' : '已接单',
        distanceDisplay: item.distance_km === null ? '距离待定位' : `${item.distance_km} km`
      })) })
    } catch (err) {
      wx.showToast({ title: err.detail || '订单加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  onEmployeeChange(e) {
    const selectedEmployeeIndex = Number(e.detail.value)
    const employee = this.data.employees[selectedEmployeeIndex]
    wx.setStorageSync('employeeId', employee.id)
    this.setData({ selectedEmployeeIndex, selectedEmployeeId: employee.id }, () => this.loadOrders())
  },

  onTabChange(e) {
    const activeTab = e.currentTarget.dataset.tab
    if (activeTab === this.data.activeTab) return
    this.setData({ activeTab }, () => this.loadOrders())
  },

  acceptOrder(e) {
    const orderId = Number(e.currentTarget.dataset.id)
    wx.showModal({
      title: '确认接单',
      content: '接单后将显示在我的订单中。',
      success: async (result) => {
        if (!result.confirm) return
        this.setData({ acceptingId: orderId })
        try {
          await this.request(`/api/employee/orders/${orderId}/accept`, {
            method: 'POST',
            data: { employee_id: this.data.selectedEmployeeId }
          })
          wx.showToast({ title: '接单成功', icon: 'success' })
          this.loadOrders()
        } catch (err) {
          wx.showToast({ title: err.detail || '接单失败，请刷新订单', icon: 'none' })
          this.loadOrders()
        } finally {
          this.setData({ acceptingId: null })
        }
      }
    })
  }
})
