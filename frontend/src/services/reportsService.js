import api from './api';

export const reportsService = {
  sales: (companyId, dateFrom, dateTo) =>
    api.get('/reports/sales', { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }),
  purchases: (companyId, dateFrom, dateTo) =>
    api.get('/reports/purchases', { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }),
  profit: (companyId, dateFrom, dateTo) =>
    api.get('/reports/profit', { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }),
  inventory: (companyId) =>
    api.get('/reports/inventory', { params: { company_id: companyId } }),
  tax: (companyId, dateFrom, dateTo) =>
    api.get('/reports/tax', { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }),
};
