const { request } = require('../../utils/api')

Page({
  data: {
    message: '',
    anonymous: false,
    submitting: false,
    loading: false,
    leftBottles: [],
    rightBottles: [],
    empty: false
  },

  onShow() {
    this.loadBottles()
  },

  onMessageInput(e) {
    this.setData({ message: e.detail.value })
  },

  onAnonymousChange(e) {
    this.setData({ anonymous: e.detail.value })
  },

  async loadBottles() {
    this.setData({ loading: true })
    try {
      const bottles = await request('/api/bottles')
      const columns = this.toWaterfallColumns(bottles.map((item) => this.formatBottle(item)))
      this.setData({
        leftBottles: columns.left,
        rightBottles: columns.right,
        empty: bottles.length === 0
      })
    } catch (err) {
      wx.showToast({ title: '漂流瓶加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  toWaterfallColumns(bottles) {
    const columns = { left: [], right: [] }
    const heights = { left: 0, right: 0 }
    bottles.forEach((bottle) => {
      const target = heights.left <= heights.right ? 'left' : 'right'
      columns[target].push(bottle)
      heights[target] += 110 + Math.ceil(bottle.content.length / 18) * 24
    })
    return columns
  },

  formatBottle(item) {
    const createdAt = item.created_at ? new Date(item.created_at.replace(/-/g, '/')) : null
    const avatarLabel = item.author_name ? item.author_name.slice(0, 1) : '漂'
    return {
      ...item,
      avatarLabel,
      displayTime: createdAt && !Number.isNaN(createdAt.getTime())
        ? `${createdAt.getFullYear()}-${String(createdAt.getMonth() + 1).padStart(2, '0')}-${String(createdAt.getDate()).padStart(2, '0')} ${String(createdAt.getHours()).padStart(2, '0')}:${String(createdAt.getMinutes()).padStart(2, '0')}`
        : ''
    }
  },

  getAuthorProfile() {
    const app = getApp()
    const profile = app.globalData.userInfo || wx.getStorageSync('userInfo') || {}
    return {
      author_name: profile.nickName || profile.name || '小陪用户',
      author_avatar: profile.avatarUrl || profile.avatar || null
    }
  },

  async sendBottle() {
    const content = this.data.message.trim()
    if (!content) {
      wx.showToast({ title: '请写下想说的话', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    try {
      const result = await request('/api/bottles', {
        method: 'POST',
        data: {
          content,
          is_anonymous: this.data.anonymous,
          ...this.getAuthorProfile()
        }
      })
      this.setData({ message: '' })
      wx.showToast({
        title: result.status === 'pending' ? '已提交，等待审核' : '漂流瓶已放出',
        icon: 'success'
      })
      if (result.status === 'published') this.loadBottles()
    } catch (err) {
      wx.showToast({ title: err.detail || '发布失败，请稍后重试', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  }
})
