function request(path, options = {}) {
  const app = getApp()
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.apiBaseUrl}${path}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'content-type': 'application/json',
        ...(options.header || {})
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
          return
        }
        reject(res.data || {})
      },
      fail: reject
    })
  })
}

function getSavedOrders() {
  return wx.getStorageSync('customerOrders') || []
}

function getSavedOrder(orderId) {
  return getSavedOrders().find((item) => item.id === Number(orderId))
}

function getSavedMallOrders() {
  return wx.getStorageSync('mallOrders') || []
}

function getSavedMallOrder(orderId) {
  return getSavedMallOrders().find((item) => item.id === Number(orderId))
}

function saveMallOrder(order) {
  const savedOrders = getSavedMallOrders().filter((item) => item.id !== order.id)
  savedOrders.unshift({ id: order.id, token: order.access_token })
  wx.setStorageSync('mallOrders', savedOrders)
}

function saveCustomerOrder(order) {
  const savedOrders = getSavedOrders()
  if (!savedOrders.some((item) => item.id === order.id)) {
    savedOrders.unshift({ id: order.id, token: order.review_token })
    wx.setStorageSync('customerOrders', savedOrders)
  }
}

function getSavedSupportTickets() {
  return wx.getStorageSync('supportTickets') || []
}

function getSavedSupportTicket(ticketId) {
  return getSavedSupportTickets().find((item) => item.id === Number(ticketId))
}

function getLatestSupportTicket(category) {
  return getSavedSupportTickets().find((item) => item.category === category) || null
}

function saveSupportTicket(ticket) {
  const tickets = getSavedSupportTickets().filter((item) => item.id !== ticket.id)
  tickets.unshift({ id: ticket.id, token: ticket.access_token, category: ticket.category })
  wx.setStorageSync('supportTickets', tickets)
}

function createSupportTicket(payload) {
  return request('/api/support/tickets', { method: 'POST', data: payload })
}

function fetchSupportTicket(saved) {
  return request(`/api/support/tickets/${saved.id}?token=${encodeURIComponent(saved.token)}`)
}

function fetchSupportMessages(saved, afterId = 0) {
  return request(`/api/support/tickets/${saved.id}/messages?token=${encodeURIComponent(saved.token)}&after_id=${afterId}`)
}

function sendSupportMessage(saved, content) {
  return request(`/api/support/tickets/${saved.id}/messages?token=${encodeURIComponent(saved.token)}`, {
    method: 'POST',
    data: { content }
  })
}

function formatDateTime(value) {
  return value ? value.replace('T', ' ').slice(0, 16) : ''
}

function formatPrice(priceCents) {
  if (priceCents === null || priceCents === undefined) return ''
  return `¥${(priceCents / 100).toFixed(2)}`
}

function statusText(status, completionType) {
  if (completionType === 'negotiated_early') return '经协商提前结束'
  if (completionType === 'system_confirmed') return '由系统确认，订单结束'
  return {
    pending: '待接单',
    accepted: '已接单',
    in_progress: '服务中',
    completed: '服务已完成',
    stopped: '订单已停止'
  }[status] || status
}

function mineStatusIndex(order) {
  if (order.status === 'pending') return 1
  if (order.status === 'accepted' || order.status === 'in_progress') return 2
  if (order.status === 'completed' && !order.review) return 3
  return 0
}

function visitStatus(order) {
  return order.status === 'completed' || order.status === 'stopped' ? 'done' : 'ongoing'
}

function normalizeCustomerOrder(order, token) {
  return {
    ...order,
    token,
    no: order.order_no,
    orderNo: order.order_no,
    type: order.service_name || '陪诊服务',
    typeName: order.service_name || '陪诊服务',
    hospital: order.hospital_name || '医院待确认',
    address: order.address_detail || '地址待确认',
    dept: order.note || '未填写',
    time: formatDateTime(order.appointment_time),
    doctor: order.employee_name || '待接单',
    phone: order.employee_phone || '',
    price: order.service_price_cents ? (order.service_price_cents / 100).toFixed(2) : '',
    statusText: order.status_text || statusText(order.status, order.completion_type),
    rawStatus: order.status,
    visitStatus: visitStatus(order),
    statusIdx: mineStatusIndex(order),
    appointmentDisplay: formatDateTime(order.appointment_time),
    displayPrice: formatPrice(order.service_price_cents),
    canReview: order.status === 'completed' && !order.review,
    earlyFinish: order.early_finish || null
  }
}

async function fetchCustomerOrder(saved) {
  const order = await request(`/api/customer/orders/${saved.id}?token=${encodeURIComponent(saved.token)}`)
  return normalizeCustomerOrder(order, saved.token)
}

async function fetchCustomerOrderMessages(saved, afterId = 0) {
  return request(
    `/api/customer/orders/${saved.id}/messages?token=${encodeURIComponent(saved.token)}&after_id=${afterId}`
  )
}

async function sendCustomerOrderMessage(saved, content) {
  return request(`/api/customer/orders/${saved.id}/messages?token=${encodeURIComponent(saved.token)}`, {
    method: 'POST',
    data: { content }
  })
}

async function fetchCustomerOrders() {
  const savedOrders = getSavedOrders()
  const orders = await Promise.all(savedOrders.map(async (saved) => {
    try {
      return await fetchCustomerOrder(saved)
    } catch (err) {
      return null
    }
  }))
  return orders.filter(Boolean)
}

async function fetchMallOrder(saved) {
  return request(`/api/mall/orders/${saved.id}?token=${encodeURIComponent(saved.token)}`)
}

async function fetchMallOrders() {
  const savedOrders = getSavedMallOrders()
  const orders = await Promise.all(savedOrders.map(async (saved) => {
    try {
      const order = await fetchMallOrder(saved)
      return { ...order, token: saved.token }
    } catch (err) {
      return null
    }
  }))
  return orders.filter(Boolean)
}

module.exports = {
  request,
  getSavedOrders,
  getSavedOrder,
  getSavedMallOrders,
  getSavedMallOrder,
  saveCustomerOrder,
  saveMallOrder,
  getSavedSupportTicket,
  getLatestSupportTicket,
  saveSupportTicket,
  createSupportTicket,
  fetchSupportTicket,
  fetchSupportMessages,
  sendSupportMessage,
  fetchCustomerOrder,
  fetchCustomerOrderMessages,
  fetchCustomerOrders,
  fetchMallOrder,
  fetchMallOrders,
  sendCustomerOrderMessage,
  formatDateTime,
  formatPrice,
  statusText,
  normalizeCustomerOrder
}
