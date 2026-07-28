Page({
  data: {
    list: [
      { id: 1, name: '张陪护师', level: '金牌 · 8年', price: 268, score: 4.9, orders: 1280, avatar: '👩‍⚕️' },
      { id: 2, name: '李陪护师', level: '银牌 · 5年', price: 198, score: 4.7, orders: 956, avatar: '🧑‍⚕️' },
      { id: 3, name: '王陪护师', level: '金牌 · 6年', price: 238, score: 4.8, orders: 1062, avatar: '👨‍⚕️' }
    ]
  },
  select(e) {
    wx.showToast({ title: '已选 ' + e.currentTarget.dataset.name, icon: 'none' })
  }
})
