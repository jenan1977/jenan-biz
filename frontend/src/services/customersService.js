import api from './api';

export const customersService = {
  create: (data) => api.post('/customers/', data),
  list: (companyId) => api.get('/customers/', { params: { company_id: companyId } }),
  get: (id) => api.get(`/customers/${id}`),
  update: (id, data) => api.put(`/customers/${id}`, data),
  delete: (id) => api.delete(`/customers/${id}`),
};
