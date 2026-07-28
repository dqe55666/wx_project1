Page({
  data: {
    rating: 5,
    tags: [],
    content: '',
    tagOptions: ['专业耐心', '准时到达', '细致入微', '服务热情', '经验丰富', '沟通顺畅']
  },
  setRating(e) { this.setData({ rating: Number(e.currentTarget.dataset.r) }) },
  toggleTag(e) {
    const t = e.currentTarget.dataset.t
    const list = this.data.tags.includes(t)
      ? this.data.tags.filter(x => x !== t)
      : [...this.data.tags, t]
    this.setData({ tags: list })
  },
  onInput(e) { this.setData({ content: e.detail.value }) },
  submit() {
    if (!this.data.content) { wx.showToast({ title: '请填写评价内容', icon: 'none' }); return }
    wx.showLoading({ title: '提交中...' })
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({ title: '评价成功（壳子）', icon: 'success' })
      setTimeout(() => wx.navigateBack({ delta: 1 }), 600)
    }, 500)
  }
})
