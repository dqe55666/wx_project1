Page({
  data: {
    entries: [
      {
        title: '预约陪护',
        desc: '选择医院单位与服务项目，提交上门陪护需求',
        url: '/pages/booking/booking',
        tone: 'primary'
      },
      {
        title: '我的',
        desc: '查看预约记录、评价服务与管理常用信息',
        url: '/pages/mine/mine',
        tone: 'mint'
      },
      {
        title: '每日知识',
        desc: '学习陪护、康复与居家护理小知识',
        url: '/pages/knowledge/knowledge',
        tone: 'sun'
      },
      {
        title: '漂瓶',
        desc: '写下心情或捞取一条温柔留言',
        url: '/pages/bottle/bottle',
        tone: 'sea'
      }
    ]
  },

  openEntry(e) {
    const { url } = e.currentTarget.dataset
    if (url) {
      wx.navigateTo({ url })
    }
  }
})
