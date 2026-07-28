Page({
  data: {
    order: {
      no: 'PZ580579578903',
      type: 'VIP陪诊',
      hospital: '张家界市人民医院',
      address: '张家界市永定区古庸路192号',
      dept: '消化内科',
      time: '2023-12-01  13:00-16:30',
      doctor: '张三',
      phone: '18812345678',
      price: 1280,
      status: '进行中'
    }
  },
  callPhone() { wx.makePhoneCall({ phoneNumber: this.data.order.phone }).catch(() => {}) },
  chat() { wx.navigateTo({ url: '/pages/message/chat' }) }
})
