import api from './api';

export const productsService = {
  create: (data) => api.post('/products/', data),
  list: (companyId) => api.get('/products/', { params: { company_id: companyId } }),
  lowStock: (companyId) => api.get('/products/low-stock', { params: { company_id: companyId } }),
  get: (id) => api.get(`/products/${id}`),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};
