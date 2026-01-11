import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add session ID to requests
let sessionId = localStorage.getItem('sessionId')
if (!sessionId) {
  sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  localStorage.setItem('sessionId', sessionId)
}

api.interceptors.request.use((config) => {
  config.headers['X-Session-ID'] = sessionId
  return config
})

export const analysisApi = {
  analyze: async (data) => {
    const response = await api.post('/api/v1/analyze', data)
    return response.data
  },

  getMetricsInfo: async () => {
    const response = await api.get('/api/v1/metrics/info')
    return response.data
  },

  getHistory: async (params = {}) => {
    const response = await api.get('/api/v1/history', { params })
    return response.data
  },

  getUserStats: async (userId) => {
    const response = await api.get(`/api/v1/stats/user/${userId}`)
    return response.data
  },

  getSystemStats: async () => {
    const response = await api.get('/api/v1/stats/system')
    return response.data
  },

  healthCheck: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api
