Page({
  data: {
    orderNo: 'SO' + Date.now(),
    amount: 1880,
    items: [
      { id: 1, name: '医用护理床', spec: '标准款 / 单摇', price: 1880, count: 1 }
    ]
  },
  onLoad() {
    const d = new Date()
    const pad = n => n < 10 ? '0' + n : '' + n
    const currentTime = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
    this.setData({ currentTime })
  },
  goPay() { wx.navigateTo({ url: '/pages/mall/pay' }) }
})
