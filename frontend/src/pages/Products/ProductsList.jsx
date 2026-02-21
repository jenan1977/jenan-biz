import React, { useEffect, useState } from 'react';
import { useCompany } from '../../hooks/useCompany';
import { productsService } from '../../services/productsService';
import DataTable from '../../components/Common/DataTable';
import Modal from '../../components/Common/Modal';
import ProductForm from './ProductForm';

export default function ProductsList() {
  const { currentCompany } = useCompany();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editProduct, setEditProduct] = useState(null);

  const loadProducts = async () => {
    if (!currentCompany?.id) return;
    setLoading(true);
    try {
      const res = await productsService.list(currentCompany.id);
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadProducts(); }, [currentCompany]);

  const handleDelete = async (id) => {
    if (!window.confirm('هل تريد حذف هذا المنتج؟')) return;
    await productsService.delete(id);
    loadProducts();
  };

  const columns = [
    { key: 'name', label: 'اسم المنتج' },
    { key: 'sku', label: 'رمز المنتج' },
    { key: 'stock_quantity', label: 'الكمية' },
    { key: 'selling_price', label: 'سعر البيع', render: (v) => `${v} ر.س` },
    { key: 'status', label: 'الحالة', render: (v) => (
      <span className={`badge badge-${v === 'active' ? 'success' : 'warning'}`}>{v}</span>
    )},
    { key: 'actions', label: 'الإجراءات', render: (_, row) => (
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
          onClick={() => { setEditProduct(row); setShowForm(true); }}>تعديل</button>
        <button className="btn btn-danger" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
          onClick={() => handleDelete(row.id)}>حذف</button>
      </div>
    )},
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>المنتجات</h1>
        <button className="btn btn-primary" onClick={() => { setEditProduct(null); setShowForm(true); }}>
          + إضافة منتج
        </button>
      </div>
      <div className="card">
        <DataTable columns={columns} data={products} loading={loading} emptyMessage="لا توجد منتجات" />
      </div>
      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title={editProduct ? 'تعديل منتج' : 'إضافة منتج'}>
        <ProductForm
          product={editProduct}
          companyId={currentCompany?.id}
          onSuccess={() => { setShowForm(false); loadProducts(); }}
        />
      </Modal>
    </div>
  );
}
