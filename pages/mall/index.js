const { request } = require('../../utils/api')

Page({
  data: {
    banners: [
      { id: 1, color: 'linear-gradient(135deg, #ff8a80, #e91e63)', title: '限时秒杀' },
      { id: 2, color: 'linear-gradient(135deg, #ffd54f, #ff8a00)', title: '新人专享' }
    ],
    categories: [
      { id: 1, icon: '🩺', name: '护理用品' },
      { id: 2, icon: '🦯', name: '康复器械' },
      { id: 3, icon: '🩹', name: '日常防护' },
      { id: 4, icon: '🔍', name: '全部' }
    ],
    hot: [],
    activeCategory: '全部',
    loading: true
  },

  onShow() {
    this.loadProducts()
  },

  async loadProducts() {
    this.setData({ loading: true })
    const category = this.data.activeCategory === '全部' ? '' : this.data.activeCategory
    try {
      const products = await request(`/api/products${category ? `?category=${encodeURIComponent(category)}` : ''}`)
      this.setData({
        hot: products.map((item) => ({
          ...item,
          price: (item.price_cents / 100).toFixed(2),
          sales: item.sales_count,
          stockText: item.stock > 0 ? `库存 ${item.stock}` : '暂时缺货',
          soldOut: item.stock < 1
        })),
        loading: false
      })
    } catch (err) {
      this.setData({ hot: [], loading: false })
      wx.showToast({ title: '商品加载失败，请稍后重试', icon: 'none' })
    }
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/mall/detail?id=' + id })
  },

  goCategory(e) {
    this.setData({ activeCategory: e.currentTarget.dataset.name }, () => this.loadProducts())
  }
})
