// KhedutMitra AI — API Service Layer
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Inject auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('km_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('km_token')
      localStorage.removeItem('km_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

// ─── Auth ───────────────────────────────────────────────────
export const authService = {
  register: (data: object) => api.post('/auth/register', data),
  login: (phone: string, password: string) => api.post('/auth/login', { phone, password }),
  me: () => api.get('/auth/me'),
}

// ─── Farmer ─────────────────────────────────────────────────
export const farmerService = {
  getDashboard: () => api.get('/farmer/dashboard'),
  getInventory: () => api.get('/farmer/inventory'),
  createInventory: (data: object) => api.post('/farmer/inventory', data),
  updateInventory: (id: string, data: object) => api.put(`/farmer/inventory/${id}`, data),
  deleteInventory: (id: string) => api.delete(`/farmer/inventory/${id}`),
}

// ─── Markets ─────────────────────────────────────────────────
export const marketService = {
  getMarkets: (district?: string) => api.get('/markets', { params: { district } }),
  getCrops: () => api.get('/markets/crops'),
  getPrices: (cropId: string, marketId?: string, district?: string) =>
    api.get('/markets/prices', { params: { crop_id: cropId, market_id: marketId, district } }),
  getPriceTrend: (cropId: string, marketId: string, days = 30) =>
    api.get('/markets/prices/trend', { params: { crop_id: cropId, market_id: marketId, days } }),
  getForecast: (cropId: string, marketId: string) =>
    api.get('/markets/prices/forecast', { params: { crop_id: cropId, market_id: marketId } }),
}

// ─── AI / Agents ─────────────────────────────────────────────
export const aiService = {
  chat: (data: object) => api.post('/ai/chat', data),
  getRecommendation: (data: object) => api.post('/ai/recommendation', data),
  matchBuyers: (params: object) => api.post('/ai/match-buyers', null, { params }),
  getForecast: (cropId: string, marketId: string, horizonDays = 7) =>
    api.post('/ai/forecast', null, { params: { crop_id: cropId, market_id: marketId, horizon_days: horizonDays } }),
  qualityAssessment: (formData: FormData) =>
    api.post('/ai/quality-assessment', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  demoScenario: (cropId = 'crop_cotton', quantity = 50, district = 'Ahmedabad') =>
    api.get('/ai/demo-scenario', { params: { crop_id: cropId, quantity, district } }),
  getRecommendationHistory: (limit = 20) => api.get('/ai/recommendations', { params: { limit } }),
}

// ─── Buyers ──────────────────────────────────────────────────
export const buyerService = {
  listBuyers: (cropId?: string, district?: string) =>
    api.get('/buyers', { params: { crop_id: cropId, district } }),
  getMatches: (params: object) => api.get('/buyers/matches', { params }),
  createOffer: (data: object) => api.post('/buyers/offers', data),
  updateOffer: (id: string, status: string) => api.put(`/buyers/offers/${id}`, null, { params: { new_status: status } }),
  listOffers: () => api.get('/buyers/offers'),
  createListing: (data: object) => api.post('/buyers/listings', data),
}

// ─── Admin ────────────────────────────────────────────────────
export const adminService = {
  getHealth: () => api.get('/admin/system-health'),
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: (role?: string) => api.get('/admin/users', { params: { role } }),
}
