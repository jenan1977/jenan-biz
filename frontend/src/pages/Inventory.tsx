import React, { useEffect, useState } from 'react'
import api from '../api/axios'
import type { Product, StockMovement } from '../types'

const Inventory: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [movements, setMovements] = useState<StockMovement[]>([])
  const [loading, setLoading] = useState(true)
  const [movLoading, setMovLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [adjForm, setAdjForm] = useState({ product_id: '', quantity: 1, direction: 'add', notes: '' })
  const [saving, setSaving] = useState(false)
  const [filterProduct, setFilterProduct] = useState('')

  const fetchAll = () => {
    setLoading(true); setMovLoading(true)
    api.get('/products/').then(r => setProducts(r.data)).catch(() => setError('تعذر تحميل المنتجات')).finally(() => setLoading(false))
    api.get('/inventory/movements/').then(r => setMovements(r.data)).catch(() => {}).finally(() => setMovLoading(false))
  }
  useEffect(() => { fetchAll() }, [])

  const handleAdjust = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!adjForm.product_id) { setError('يرجى اختيار المنتج'); return }
    setSaving(true); setError('')
    try {
      await api.post('/inventory/adjust', {
        product_id: +adjForm.product_id,
        quantity: adjForm.direction === 'add' ? adjForm.quantity : -adjForm.quantity,
        notes: adjForm.notes,
      })
      setSuccess('تم تعديل المخزون بنجاح')
      setAdjForm({ product_id: '', quantity: 1, direction: 'add', notes: '' })
      fetchAll(); setTimeout(() => setSuccess(''), 3000)
    } catch { setError('حدث خطأ أثناء التعديل') }
    finally { setSaving(false) }
  }

  const filteredMovements = filterProduct
    ? movements.filter(m => String(m.product_id) === filterProduct)
    : movements

  const inp = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500'

  return (
    <div dir="rtl" className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">إدارة المخزون</h2>

      {error && <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
      {success && <div className="bg-green-50 border border-green-300 text-green-700 px-4 py-2 rounded-lg text-sm">{success}</div>}

      {/* Stock Report */}
      <div className="bg-white rounded-xl shadow">
        <div className="px-6 py-4 border-b"><h3 className="text-lg font-semibold text-gray-700">تقرير المخزون</h3></div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex justify-center p-10"><svg className="animate-spin w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" /></svg></div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>{['المنتج','الرمز','الكمية الحالية','الحد الأدنى','الحالة'].map(h => <th key={h} className="px-4 py-3 text-right text-gray-600 font-medium">{h}</th>)}</tr>
              </thead>
              <tbody>
                {products.length === 0 ? <tr><td colSpan={5} className="text-center py-8 text-gray-400">لا توجد منتجات</td></tr>
                : products.map(p => {
                  const isLow = p.stock_quantity <= p.min_stock_level
                  return (
                    <tr key={p.id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium">{p.name}</td>
                      <td className="px-4 py-3 text-gray-500">{p.sku}</td>
                      <td className="px-4 py-3 font-semibold">{p.stock_quantity} {p.unit}</td>
                      <td className="px-4 py-3 text-gray-500">{p.min_stock_level}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${isLow ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                          {isLow ? 'منخفض' : 'مناسب'}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Manual Adjustment */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">تعديل يدوي للمخزون</h3>
        <form onSubmit={handleAdjust} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">المنتج *</label>
            <select className={inp} value={adjForm.product_id} onChange={e => setAdjForm({...adjForm, product_id: e.target.value})} required>
              <option value="">اختر المنتج</option>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الكمية</label>
            <input type="number" min="1" className={inp} value={adjForm.quantity} onChange={e => setAdjForm({...adjForm, quantity: +e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">العملية</label>
            <select className={inp} value={adjForm.direction} onChange={e => setAdjForm({...adjForm, direction: e.target.value})}>
              <option value="add">إضافة (+)</option>
              <option value="sub">خصم (-)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
            <input className={inp} value={adjForm.notes} onChange={e => setAdjForm({...adjForm, notes: e.target.value})} placeholder="اختياري" />
          </div>
          <div className="sm:col-span-4 flex justify-end">
            <button type="submit" disabled={saving} className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm disabled:opacity-60">
              {saving ? 'جاري التعديل...' : 'تطبيق التعديل'}
            </button>
          </div>
        </form>
      </div>

      {/* Stock Movements */}
      <div className="bg-white rounded-xl shadow">
        <div className="px-6 py-4 border-b flex items-center justify-between flex-wrap gap-3">
          <h3 className="text-lg font-semibold text-gray-700">حركات المخزون</h3>
          <select className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            value={filterProduct} onChange={e => setFilterProduct(e.target.value)}>
            <option value="">كل المنتجات</option>
            {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div className="overflow-x-auto">
          {movLoading ? (
            <div className="flex justify-center p-10"><svg className="animate-spin w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" /></svg></div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>{['المنتج','النوع','الكمية','المرجع','الملاحظات','التاريخ'].map(h => <th key={h} className="px-4 py-3 text-right text-gray-600 font-medium">{h}</th>)}</tr>
              </thead>
              <tbody>
                {filteredMovements.length === 0 ? <tr><td colSpan={6} className="text-center py-8 text-gray-400">لا توجد حركات</td></tr>
                : filteredMovements.map(m => (
                  <tr key={m.id} className="border-t border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">{m.product_name || m.product_id}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        m.movement_type === 'purchase' ? 'bg-blue-100 text-blue-700'
                        : m.movement_type === 'sale' ? 'bg-red-100 text-red-700'
                        : 'bg-gray-100 text-gray-600'
                      }`}>
                        {m.movement_type === 'purchase' ? 'مشتريات' : m.movement_type === 'sale' ? 'مبيعات' : m.movement_type}
                      </span>
                    </td>
                    <td className={`px-4 py-3 font-medium ${m.quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {m.quantity > 0 ? '+' : ''}{m.quantity}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{m.reference_id || '-'}</td>
                    <td className="px-4 py-3 text-gray-500">{m.notes || '-'}</td>
                    <td className="px-4 py-3 text-gray-500">{new Date(m.created_at).toLocaleDateString('ar-SA')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

export default Inventory
