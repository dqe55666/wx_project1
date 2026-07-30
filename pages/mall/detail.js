const { request } = require('../../utils/api')

Page({
  data: {
    product: null,
    loading: true
  },
  onLoad(options) {
    this.productId = Number(options.id)
    this.loadProduct()
  },
  async loadProduct() {
    if (!this.productId) {
      wx.showToast({ title: '商品不存在', icon: 'none' })
      return
    }
    try {
      const product = await request(`/api/products/${this.productId}`)
      this.setData({
        product: {
          ...product,
          price: (product.price_cents / 100).toFixed(2),
          sales: product.sales_count,
          stockText: product.stock > 0 ? `库存 ${product.stock} 件` : '暂时缺货',
          soldOut: product.stock < 1
        },
        loading: false
      })
    } catch (err) {
      this.setData({ loading: false })
      wx.showToast({ title: '商品已下架或不存在', icon: 'none' })
    }
  },
  goAddress() { wx.navigateTo({ url: '/pages/mall/address' }) },
  goCart() {
    if (!this.data.product || this.data.product.soldOut) return
    wx.navigateTo({ url: `/pages/mall/confirm?id=${this.data.product.id}` })
  },
  addToCart() {
    const product = this.data.product
    if (!product || product.soldOut) {
      wx.showToast({ title: '该商品暂时缺货', icon: 'none' })
      return
    }
    wx.setStorageSync('mallCartProduct', { id: product.id, count: 1 })
    wx.showToast({ title: '已加入购物车', icon: 'success' })
  },
  goMallHome() {
    wx.switchTab({ url: '/pages/mall/index', fail: () => wx.navigateBack({ delta: 1 }) })
  }
})
