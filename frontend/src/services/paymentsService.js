import api from './api';

export const paymentsService = {
  create: (data) => api.post('/payments/', data),
  list: (companyId) => api.get('/payments/', { params: { company_id: companyId } }),
  get: (id) => api.get(`/payments/${id}`),
};
