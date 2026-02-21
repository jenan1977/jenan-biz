import api from './api';

export const analyticsService = {
  heatmap: (companyId, year) =>
    api.get('/analytics/heatmap', { params: { company_id: companyId, year } }),
  topProducts: (companyId, limit = 10) =>
    api.get('/analytics/top-products', { params: { company_id: companyId, limit } }),
};
