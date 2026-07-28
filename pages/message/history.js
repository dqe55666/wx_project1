Page({
  data: { kw: '', results: [] },
  onInput(e) {
    const v = e.detail.value
    const list = v ? [
      { id: 1, text: v, time: '10:23' },
      { id: 2, text: '您提到的 ' + v + ' 已记录', time: '10:24' }
    ] : []
    this.setData({ kw: v, results: list })
  }
})
