Page({
  data: { rating: 5, content: '', tags: [] },
  setRating(e) { this.setData({ rating: Number(e.currentTarget.dataset.r) }) },
  toggleTag(e) {
    const t = e.currentTarget.dataset.t
    this.setData({ tags: this.data.tags.includes(t) ? this.data.tags.filter(x => x !== t) : [...this.data.tags, t] })
  },
  onInput(e) { this.setData({ content: e.detail.value }) },
  submit() {
    if (!this.data.content) { wx.showToast({ title: '请填写评价', icon: 'none' }); return }
    wx.showToast({ title: '评价成功（壳子）', icon: 'success' })
    setTimeout(() => wx.navigateBack({ delta: 1 }), 600)
  }
})
