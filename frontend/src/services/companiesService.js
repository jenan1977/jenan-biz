import api from './api';

export const companiesService = {
  create: (data) => api.post('/companies/', data),
  list: () => api.get('/companies/'),
  get: (id) => api.get(`/companies/${id}`),
  update: (id, data) => api.put(`/companies/${id}`, data),
  delete: (id) => api.delete(`/companies/${id}`),
};
