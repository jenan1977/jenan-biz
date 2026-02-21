import React, { useState, useEffect } from 'react'
import { getProducts, createProduct, updateProduct, deleteProduct } from '../services/productsService'
import toast from 'react-hot-toast'
import { Plus, Pencil, Trash2, X } from 'lucide-react'

const emptyForm = { name: '', description: '', sku: '', purchase_price: '', sale_price: '', unit: '', category: '', min_stock: '' }

export default function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [editId, setEditId] = useState(null)
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    getProducts().then(r => setProducts(r.data)).catch(() => toast.error('خطأ في تحميل المنتجات')).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const openAdd = () => { setForm(emptyForm); setEditId(null); setShowModal(true) }
  const openEdit = (p) => { setForm({ name: p.name || '', description: p.description || '', sku: p.sku || '', purchase_price: p.purchase_price ?? '', sale_price: p.sale_price ?? '', unit: p.unit || '', category: p.category || '', min_stock: p.min_stock ?? '' }); setEditId(p.id); setShowModal(true) }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const data = { ...form, purchase_price: Number(form.purchase_price), sale_price: Number(form.sale_price), min_stock: Number(form.min_stock) }
      if (editId) { await updateProduct(editId, data); toast.success('تم تحديث المنتج') }
      else { await createProduct(data); toast.success('تم إضافة المنتج') }
      setShowModal(false); load()
    } catch { toast.error('حدث خطأ') } finally { setSaving(false) }
  }

  const handleDelete = async (id) => {
    if (!confirm('هل تريد حذف هذا المنتج؟')) return
    try { await deleteProduct(id); toast.success('تم الحذف'); load() } catch { toast.error('خطأ في الحذف') }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">المنتجات</h2>
        <button onClick={openAdd} className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
          <Plus size={18} /><span>إضافة منتج</span>
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div></div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['الاسم','الكود','سعر الشراء','سعر البيع','الوحدة','الفئة','الحد الأدنى','إجراءات'].map(h => (
                  <th key={h} className="text-right px-4 py-3 text-gray-600 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {products.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-10 text-gray-400">لا توجد منتجات</td></tr>
              ) : products.map(p => (
                <tr key={p.id} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 font-medium text-gray-800">{p.name}</td>
                  <td className="px-4 py-3 text-gray-600">{p.sku || '-'}</td>
                  <td className="px-4 py-3 text-gray-600">{p.purchase_price}</td>
                  <td className="px-4 py-3 text-gray-600">{p.sale_price}</td>
                  <td className="px-4 py-3 text-gray-600">{p.unit || '-'}</td>
                  <td className="px-4 py-3 text-gray-600">{p.category || '-'}</td>
                  <td className="px-4 py-3 text-gray-600">{p.min_stock ?? '-'}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => openEdit(p)} className="text-indigo-600 hover:text-indigo-800 p-1"><Pencil size={16} /></button>
                      <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:text-red-700 p-1"><Trash2 size={16} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h3 className="text-lg font-bold text-gray-800">{editId ? 'تعديل المنتج' : 'إضافة منتج جديد'}</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {[
                { key: 'name', label: 'الاسم', required: true },
                { key: 'description', label: 'الوصف' },
                { key: 'sku', label: 'الكود (SKU)' },
                { key: 'purchase_price', label: 'سعر الشراء', type: 'number' },
                { key: 'sale_price', label: 'سعر البيع', type: 'number' },
                { key: 'unit', label: 'الوحدة' },
                { key: 'category', label: 'الفئة' },
                { key: 'min_stock', label: 'الحد الأدنى للمخزون', type: 'number' },
              ].map(({ key, label, type = 'text', required }) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input
                    type={type}
                    value={form[key]}
                    onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                    required={required}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  />
                </div>
              ))}
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={saving} className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg hover:bg-indigo-700 transition disabled:opacity-60">
                  {saving ? 'جاري الحفظ...' : 'حفظ'}
                </button>
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-gray-100 text-gray-700 py-2.5 rounded-lg hover:bg-gray-200 transition">إلغاء</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
