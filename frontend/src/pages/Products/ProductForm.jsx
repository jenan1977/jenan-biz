import React, { useState } from 'react';
import { productsService } from '../../services/productsService';
import { useNotification } from '../../hooks/useNotification';

export default function ProductForm({ product, companyId, onSuccess }) {
  const notify = useNotification();
  const [form, setForm] = useState({
    name: product?.name || '',
    sku: product?.sku || '',
    selling_price: product?.selling_price || 0,
    cost_price: product?.cost_price || 0,
    stock_quantity: product?.stock_quantity || 0,
    min_stock_level: product?.min_stock_level || 5,
    unit: product?.unit || 'piece',
    status: product?.status || 'active',
    company_id: companyId,
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (product) {
        await productsService.update(product.id, form);
        notify.success('تم تحديث المنتج');
      } else {
        await productsService.create({ ...form, company_id: companyId });
        notify.success('تم إضافة المنتج');
      }
      onSuccess?.();
    } catch (err) {
      notify.error(err.response?.data?.detail || 'خطأ في حفظ المنتج');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { name: 'name', label: 'اسم المنتج', type: 'text' },
    { name: 'sku', label: 'رمز المنتج (SKU)', type: 'text' },
    { name: 'cost_price', label: 'سعر التكلفة', type: 'number' },
    { name: 'selling_price', label: 'سعر البيع', type: 'number' },
    { name: 'stock_quantity', label: 'الكمية', type: 'number' },
    { name: 'min_stock_level', label: 'الحد الأدنى للمخزون', type: 'number' },
    { name: 'unit', label: 'وحدة القياس', type: 'text' },
  ];

  return (
    <form onSubmit={handleSubmit}>
      {fields.map((f) => (
        <div key={f.name} className="form-group">
          <label className="form-label">{f.label}</label>
          <input className="form-input" type={f.type} name={f.name} value={form[f.name]} onChange={handleChange} />
        </div>
      ))}
      <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
        {loading ? 'جاري الحفظ...' : 'حفظ'}
      </button>
    </form>
  );
}
