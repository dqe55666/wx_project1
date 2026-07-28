Page({
  data: {
    selected: 0,
    list: [
      { id: 1, name: '张三', phone: '18812345678', region: '湖南省张家界市永定区', detail: '古庸路 192 号', tag: '家' },
      { id: 2, name: '李四', phone: '13987654321', region: '湖南省张家界市永定区', detail: '解放路 50 号', tag: '公司' }
    ]
  },
  select(e) { this.setData({ selected: e.currentTarget.dataset.i }) },
  add() { wx.navigateTo({ url: '/pages/mall/address-add' }) },
  edit() { wx.navigateTo({ url: '/pages/mall/address-add' }) }
})
