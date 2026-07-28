Page({
  data: {
    name: '医用护理床',
    cover: '🛏️',
    spec: '标准款 / 单摇',
    price: 1880,
    count: 1,
    address: { name: '张三', phone: '18812345678', region: '湖南省张家界市永定区', detail: '古庸路 192 号' }
  },
  goAddress() { wx.navigateTo({ url: '/pages/mall/address' }) },
  submit() { wx.navigateTo({ url: '/pages/mall/pay' }) }
})
