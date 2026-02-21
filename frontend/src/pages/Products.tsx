import React, { useEffect, useState } from 'react'
import api from '../api/axios'
import type { Product } from '../types'
import { PlusIcon, PencilIcon, TrashIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

const emptyProduct: Omit<Product, 'id'> = {
  name: '', sku: '', description: '', cost_price: 0, selling_price: 0,
  stock_quantity: 0, min_stock_level: 0, category: '', unit: 'قطعة', is_active: true,
}

const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Product | null>(null)
  const [form, setForm] = useState<Omit<Product, 'id'>>(emptyProduct)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [saving, setSaving] = useState(false)

  const fetchProducts = () => {
    setLoading(true)
    api.get('/products/')
      .then((r) => setProducts(r.data))
      .catch(() => setError('تعذر تحميل المنتجات'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchProducts() }, [])

  const openAdd = () => { setEditing(null); setForm(emptyProduct); setShowModal(true) }
  const openEdit = (p: Product) => {
    setEditing(p)
    setForm({ name: p.name, sku: p.sku, description: p.description||'', cost_price: p.cost_price,
      selling_price: p.selling_price, stock_quantity: p.stock_quantity, min_stock_level: p.min_stock_level,
      category: p.category||'', unit: p.unit, is_active: p.is_active })
    setShowModal(true)
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim() || !form.sku.trim()) { setError('الاسم والرمز مطلوبان'); return }
    setSaving(true); setError('')
    try {
      if (editing) { await api.put(`/products/${editing.id}`, form) }
      else { await api.post('/products/', form) }
      setSuccess(editing ? 'تم تحديث المنتج' : 'تم إضافة المنتج')
      setShowModal(false); fetchProducts()
      setTimeout(() => setSuccess(''), 3000)
    } catch { setError('حدث خطأ أثناء الحفظ') }
    finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await api.delete(`/products/${deleteId}`)
      setSuccess('تم حذف المنتج')
      setDeleteId(null); fetchProducts()
      setTimeout(() => setSuccess(''), 3000)
    } catch { setError('تعذر حذف المنتج') }
  }

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.sku.toLowerCase().includes(search.toLowerCase())
  )

  const inp = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500'

  return (
    <div dir="rtl" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">المنتجات</h2>
        <button onClick={openAdd} className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          <PlusIcon className="w-4 h-4" /> إضافة منتج
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
      {success && <div className="bg-green-50 border border-green-300 text-green-700 px-4 py-2 rounded-lg text-sm">{success}</div>}

      {/* Search */}
      <div className="relative">
        <MagnifyingGlassIcon className="w-4 h-4 absolute right-3 top-2.5 text-gray-400" />
        <input value={search} onChange={e => setSearch(e.target.value)}
          className="w-full border border-gray-300 rounded-lg pr-10 pl-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="بحث بالاسم أو الرمز..." />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow overflow-x-auto">
        {loading ? (
          <div className="flex justify-center p-10">
            <svg className="animate-spin w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {['الاسم','الرمز','الفئة','سعر التكلفة','سعر البيع','المخزون','الوحدة','الحالة','إجراءات'].map(h => (
                  <th key={h} className="px-4 py-3 text-right text-gray-600 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={9} className="text-center py-8 text-gray-400">لا توجد منتجات</td></tr>
              ) : filtered.map(p => (
                <tr key={p.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{p.name}</td>
                  <td className="px-4 py-3 text-gray-500">{p.sku}</td>
                  <td className="px-4 py-3 text-gray-500">{p.category || '-'}</td>
                  <td className="px-4 py-3">{p.cost_price.toFixed(2)}</td>
                  <td className="px-4 py-3">{p.selling_price.toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <span className={p.stock_quantity <= p.min_stock_level ? 'text-red-600 font-medium' : ''}>
                      {p.stock_quantity}
                    </span>
                  </td>
                  <td className="px-4 py-3">{p.unit}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs ${p.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                      {p.is_active ? 'نشط' : 'غير نشط'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => openEdit(p)} className="text-blue-600 hover:text-blue-800"><PencilIcon className="w-4 h-4" /></button>
                      <button onClick={() => setDeleteId(p.id)} className="text-red-500 hover:text-red-700"><TrashIcon className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">{editing ? 'تعديل المنتج' : 'إضافة منتج جديد'}</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <form onSubmit={handleSave} className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الاسم *</label>
                <input className={inp} value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الرمز (SKU) *</label>
                <input className={inp} value={form.sku} onChange={e => setForm({...form, sku: e.target.value})} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الفئة</label>
                <input className={inp} value={form.category} onChange={e => setForm({...form, category: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الوحدة</label>
                <input className={inp} value={form.unit} onChange={e => setForm({...form, unit: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">سعر التكلفة</label>
                <input type="number" step="0.01" min="0" className={inp} value={form.cost_price} onChange={e => setForm({...form, cost_price: +e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">سعر البيع</label>
                <input type="number" step="0.01" min="0" className={inp} value={form.selling_price} onChange={e => setForm({...form, selling_price: +e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الكمية في المخزون</label>
                <input type="number" min="0" className={inp} value={form.stock_quantity} onChange={e => setForm({...form, stock_quantity: +e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الحد الأدنى للمخزون</label>
                <input type="number" min="0" className={inp} value={form.min_stock_level} onChange={e => setForm({...form, min_stock_level: +e.target.value})} />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">الوصف</label>
                <textarea className={inp} rows={2} value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
              </div>
              <div className="sm:col-span-2 flex items-center gap-2">
                <input type="checkbox" id="is_active" checked={form.is_active} onChange={e => setForm({...form, is_active: e.target.checked})} className="w-4 h-4" />
                <label htmlFor="is_active" className="text-sm text-gray-700">نشط</label>
              </div>
              <div className="sm:col-span-2 flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">إلغاء</button>
                <button type="submit" disabled={saving} className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm disabled:opacity-60">
                  {saving ? 'جاري الحفظ...' : 'حفظ'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {deleteId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold mb-3">تأكيد الحذف</h3>
            <p className="text-gray-600 text-sm mb-5">هل أنت متأكد من حذف هذا المنتج؟</p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setDeleteId(null)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm">إلغاء</button>
              <button onClick={handleDelete} className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm">حذف</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Products
