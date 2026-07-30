const { request, saveMallOrder } = require('../../utils/api')

Page({
  data: {
    product: null,
    count: 1,
    address: { name: '张三', phone: '18812345678', region: '湖南省张家界市永定区', detail: '古庸路 192 号' }
  },
  onLoad(options) {
    this.productId = Number(options.id || (wx.getStorageSync('mallCartProduct') || {}).id)
    this.loadProduct()
  },
  async loadProduct() {
    if (!this.productId) {
      wx.showToast({ title: '请选择商品', icon: 'none' })
      return
    }
    try {
      const product = await request(`/api/products/${this.productId}`)
      this.setData({ product: { ...product, price: (product.price_cents / 100).toFixed(2), soldOut: product.stock < 1 } })
    } catch (err) {
      wx.showToast({ title: '商品已下架或不存在', icon: 'none' })
    }
  },
  goAddress() { wx.navigateTo({ url: '/pages/mall/address' }) },
  decrease() {
    if (this.data.count > 1) this.setData({ count: this.data.count - 1 })
  },
  increase() {
    const product = this.data.product
    if (!product) return
    if (this.data.count >= product.stock) {
      wx.showToast({ title: '已达到当前库存上限', icon: 'none' })
      return
    }
    this.setData({ count: this.data.count + 1 })
  },
  async submit() {
    const product = this.data.product
    if (!product || product.soldOut || this.data.count > product.stock) {
      wx.showToast({ title: '商品库存不足，请返回商城刷新', icon: 'none' })
      return
    }
    wx.showLoading({ title: '正在创建订单...' })
    try {
      const order = await request('/api/mall/orders', {
        method: 'POST',
        data: { product_id: product.id, quantity: this.data.count }
      })
      wx.hideLoading()
      saveMallOrder(order)
      wx.navigateTo({ url: `/pages/mall/checkout?id=${order.id}&token=${encodeURIComponent(order.access_token)}` })
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: (err && err.detail) || '创建订单失败，请稍后重试', icon: 'none' })
    }
  }
})
