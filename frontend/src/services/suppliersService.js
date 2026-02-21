import api from './api';

export const suppliersService = {
  create: (data) => api.post('/suppliers/', data),
  list: (companyId) => api.get('/suppliers/', { params: { company_id: companyId } }),
  get: (id) => api.get(`/suppliers/${id}`),
  update: (id, data) => api.put(`/suppliers/${id}`, data),
  delete: (id) => api.delete(`/suppliers/${id}`),
};
