Component({
  properties: {
    strict: { type: Boolean, value: true }
  },
  data: {
    sliderX: 0,
    trackWidth: 560,
    thumbSize: 80,
    maxX: 0,
    slotLeft: 360,
    status: 'idle',
    tipsText: '拖动滑块完成拼图',
    _startX: 0,
    _startSliderX: 0,
    _failTimer: null
  },
  lifetimes: {
    ready() {
      this._initLayout()
    }
  },
  methods: {
    _initLayout() {
      // 通过 query 获取轨道实际宽度
      const query = this.createSelectorQuery()
      query.select('#track').boundingClientRect()
      query.exec(res => {
        if (!res || !res[0]) return
        const trackWidth = Math.round(res[0].width)
        const maxX = trackWidth - this.data.thumbSize
        this.setData({ trackWidth, maxX, slotLeft: maxX + 12 })
      })
    },
    onTouchStart(e) {
      if (this.data.status === 'success') return
      this.setData({
        status: 'moving',
        tipsText: '拖动中...',
        _startX: e.touches[0].clientX,
        _startSliderX: this.data.sliderX
      })
    },
    onTouchMove(e) {
      if (this.data.status === 'success') return
      const dx = e.touches[0].clientX - this.data._startX
      let next = this.data._startSliderX + dx
      if (next < 0) next = 0
      if (next > this.data.maxX) next = this.data.maxX
      this.setData({ sliderX: next })
    },
    onTouchEnd() {
      if (this.data.status === 'success') return
      const pass = this.data.sliderX >= this.data.maxX * 0.95
      if (pass) {
        this.setData({
          sliderX: this.data.maxX,
          status: 'success',
          tipsText: '验证通过'
        })
        this.triggerEvent('success')
      } else {
        this.setData({ status: 'fail', tipsText: '验证失败，请重试' })
        this.triggerEvent('fail')
        if (this.data._failTimer) clearTimeout(this.data._failTimer)
        this.data._failTimer = setTimeout(() => {
          this.setData({ sliderX: 0, status: 'idle', tipsText: '拖动滑块完成拼图' })
        }, 700)
      }
    },
    reset() {
      if (this.data._failTimer) clearTimeout(this.data._failTimer)
      this.setData({ sliderX: 0, status: 'idle', tipsText: '拖动滑块完成拼图' })
    }
  }
})
