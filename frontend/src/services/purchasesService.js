import api from './api';

export const purchasesService = {
  create: (data) => api.post('/purchases/', data),
  list: (companyId) => api.get('/purchases/', { params: { company_id: companyId } }),
  get: (id) => api.get(`/purchases/${id}`),
};
