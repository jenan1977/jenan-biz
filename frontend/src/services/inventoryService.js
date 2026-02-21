import api from './api'
export const getStock = () => api.get('/inventory')
export const getLowStock = () => api.get('/inventory/low-stock')
export const getMovements = () => api.get('/inventory/movements')
export const adjustStock = (data) => api.post('/inventory/adjust', data)
