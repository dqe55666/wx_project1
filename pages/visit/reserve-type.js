Page({
  data: {
    types: [
      { id: 1, name: '挂号陪诊', desc: '协助挂号、引导就诊', price: 98 },
      { id: 2, name: '取药陪诊', desc: '代取药品、配送到家', price: 68 },
      { id: 3, name: '复诊陪诊', desc: '复诊取号、问诊陪同', price: 168 },
      { id: 4, name: '检查陪诊', desc: 'CT / 核磁等检查陪同', price: 198 },
      { id: 5, name: '住院陪诊', desc: '出入院手续代办', price: 268 },
      { id: 6, name: '手术陪诊', desc: '术前术后全程陪同', price: 488 }
    ],
    selected: 0
  },
  pick(e) { this.setData({ selected: e.currentTarget.dataset.i }) },
  confirm() {
    const t = this.data.types[this.data.selected]
    wx.showToast({ title: '已选 ' + t.name, icon: 'none' })
    setTimeout(() => {
      // 选完类型继续选陪诊师
      wx.redirectTo({ url: '/pages/visit/accompany' })
    }, 400)
  }
})
