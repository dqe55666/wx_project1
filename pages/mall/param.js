Page({
  data: {
    types: ['单摇', '双摇', '三摇'],
    sizes: ['标准', '加大'],
    colors: ['木纹', '白色'],
    sel: { type: 0, size: 0, color: 0 },
    count: 1
  },
  pick(e) {
    const { g, i } = e.currentTarget.dataset
    this.setData({ [`sel.${g}`]: i })
  },
  change(e) {
    const d = e.currentTarget.dataset
    let n = this.data.count + d.step
    if (n < 1) n = 1
    if (n > 99) n = 99
    this.setData({ count: n })
  },
  confirm() {
    wx.showToast({ title: '参数已选', icon: 'none' })
    setTimeout(() => wx.navigateBack({ delta: 1 }), 500)
  }
})
