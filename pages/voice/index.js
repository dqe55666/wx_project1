const recorderManager = wx.getRecorderManager()

Page({
  data: {
    recording: false,
    statusText: '点击按钮开始录音',
    duration: 0,
    result: ''
  },

  onLoad() {
    recorderManager.onStart(() => {
      this.setData({ recording: true, statusText: '正在录音，请再次点击结束' })
    })
    recorderManager.onStop((res) => {
      this.setData({
        recording: false,
        duration: Math.round((res.duration || 0) / 1000),
        statusText: '录音完成',
        result: '语音已录制，识别服务待接入'
      })
    })
    recorderManager.onError(() => {
      this.setData({ recording: false, statusText: '录音失败，请检查麦克风权限' })
      wx.showToast({ title: '无法使用麦克风', icon: 'none' })
    })
  },

  toggleRecording() {
    if (this.data.recording) {
      recorderManager.stop()
      return
    }
    this.setData({ result: '', duration: 0 })
    recorderManager.start({
      duration: 60000,
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 96000,
      format: 'mp3'
    })
  },

  onUnload() {
    if (this.data.recording) recorderManager.stop()
  }
})
