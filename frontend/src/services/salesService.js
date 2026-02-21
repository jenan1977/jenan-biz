import api from './api';

export const salesService = {
  createInvoice: (data) => api.post('/sales/invoices', data),
  listInvoices: (companyId) => api.get('/sales/invoices', { params: { company_id: companyId } }),
  getInvoice: (id) => api.get(`/sales/invoices/${id}`),
  markPaid: (id, amount) => api.post(`/sales/invoices/${id}/pay`, null, { params: { amount } }),
};
