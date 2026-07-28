Page({
  data: {
    banners: [
      { id: 1, color: 'linear-gradient(135deg, #ff8a80, #e91e63)', title: '限时秒杀' },
      { id: 2, color: 'linear-gradient(135deg, #ffd54f, #ff8a00)', title: '新人专享' }
    ],
    categories: [
      { id: 1, icon: '🩺', name: '护理用品' },
      { id: 2, icon: '💊', name: '营养保健' },
      { id: 3, icon: '🧴', name: '康复器械' },
      { id: 4, icon: '🩹', name: '日常防护' },
      { id: 5, icon: '👕', name: '护理服' },
      { id: 6, icon: '🎁', name: '礼品卡' },
      { id: 7, icon: '📦', name: '套餐' },
      { id: 8, icon: '🔍', name: '全部' }
    ],
    hot: [
      { id: 101, name: '医用护理床', price: 1880, sales: 326, cover: '🛏️' },
      { id: 102, name: '血压计（家用手腕式）', price: 268, sales: 1280, cover: '🩺' },
      { id: 103, name: '成人纸尿裤 L码', price: 89, sales: 956, cover: '🧻' },
      { id: 104, name: '助行器 可折叠', price: 198, sales: 412, cover: '🦯' }
    ]
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/mall/detail?id=' + id })
  },

  goCategory(e) {
    wx.showToast({ title: '分类（壳子）', icon: 'none' })
  }
})
