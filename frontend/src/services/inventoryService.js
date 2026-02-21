import api from './api';

export const inventoryService = {
  recordMovement: (data) => api.post('/inventory/movements', data),
  adjustStock: (data) => api.post('/inventory/adjust', data),
  getMovements: (productId) => api.get(`/inventory/movements/${productId}`),
};
