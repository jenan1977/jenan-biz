import React, { useState, useEffect } from 'react'
import { getPurchases, createPurchase, deletePurchase } from '../services/purchasesService'
import { getSuppliers } from '../services/suppliersService'
import { getProducts } from '../services/productsService'
import toast from 'react-hot-toast'
import { Plus, Trash2, X, Eye, PlusCircle, MinusCircle } from 'lucide-react'

const statusMap = { pending: 'معلقة', received: 'مستلمة', cancelled: 'ملغية' }
const statusColor = { pending: 'bg-yellow-100 text-yellow-700', received: 'bg-green-100 text-green-700', cancelled: 'bg-red-100 text-red-700' }

export default function Purchases() {
  const [purchases, setPurchases] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [viewItem, setViewItem] = useState(null)
  const [saving, setSaving] = useState(false)

  const [supplierId, setSupplierId] = useState('')
  const [lines, setLines] = useState([{ product_id: '', quantity: 1, unit_price: '' }])
  const [applyTax, setApplyTax] = useState(false)
  const [notes, setNotes] = useState('')

  const load = () => {
    setLoading(true)
    Promise.all([getPurchases(), getSuppliers(), getProducts()])
      .then(([p, s, pr]) => { setPurchases(p.data); setSuppliers(s.data); setProducts(pr.data) })
      .catch(() => toast.error('خطأ في تحميل البيانات'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const subtotal = lines.reduce((s, l) => s + (Number(l.quantity) * Number(l.unit_price) || 0), 0)
  const tax = applyTax ? subtotal * 0.15 : 0
  const total = subtotal + tax

  const addLine = () => setLines(ls => [...ls, { product_id: '', quantity: 1, unit_price: '' }])
  const removeLine = (i) => setLines(ls => ls.filter((_, idx) => idx !== i))
  const updateLine = (i, key, val) => setLines(ls => ls.map((l, idx) => idx === i ? { ...l, [key]: val } : l))

  const handleLineProductChange = (i, pid) => {
    const p = products.find(p => String(p.id) === String(pid))
    updateLine(i, 'product_id', pid)
    if (p) updateLine(i, 'unit_price', p.purchase_price ?? '')
  }

  const handleCreate = async (e) => {
    e.preventDefault(); setSaving(true)
    try {
      const data = {
        supplier_id: Number(supplierId),
        items: lines.filter(l => l.product_id).map(l => ({ product_id: Number(l.product_id), quantity: Number(l.quantity), unit_price: Number(l.unit_price) })),
        apply_tax: applyTax,
        notes,
      }
      await createPurchase(data)
      toast.success('تم إنشاء فاتورة المشتريات')
      setShowCreate(false); setSupplierId(''); setLines([{ product_id: '', quantity: 1, unit_price: '' }]); setApplyTax(false); setNotes('')
      load()
    } catch { toast.error('حدث خطأ في الإنشاء') } finally { setSaving(false) }
  }

  const handleDelete = async (id) => {
    if (!confirm('هل تريد حذف هذه الفاتورة؟')) return
    try { await deletePurchase(id); toast.success('تم الحذف'); load() } catch { toast.error('خطأ في الحذف') }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">فواتير المشتريات</h2>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
          <Plus size={18} /><span>فاتورة جديدة</span>
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div></div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['رقم الفاتورة','المورد','التاريخ','الإجمالي','الضريبة','المجموع الكلي','الحالة','إجراءات'].map(h => (
                  <th key={h} className="text-right px-4 py-3 text-gray-600 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {purchases.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-10 text-gray-400">لا توجد فواتير</td></tr>
              ) : purchases.map(p => (
                <tr key={p.id} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 font-medium text-indigo-700">#{p.invoice_number || p.id}</td>
                  <td className="px-4 py-3 text-gray-700">{suppliers.find(s => s.id === p.supplier_id)?.name || p.supplier_id}</td>
                  <td className="px-4 py-3 text-gray-600">{p.date ? new Date(p.date).toLocaleDateString('ar-SA') : '-'}</td>
                  <td className="px-4 py-3 text-gray-600">{(p.subtotal ?? 0).toFixed(2)}</td>
                  <td className="px-4 py-3 text-gray-600">{(p.tax_amount ?? 0).toFixed(2)}</td>
                  <td className="px-4 py-3 font-semibold text-gray-800">{(p.total_amount ?? 0).toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor[p.status] || 'bg-gray-100 text-gray-700'}`}>
                      {statusMap[p.status] || p.status || '-'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => setViewItem(p)} className="text-blue-500 hover:text-blue-700 p-1"><Eye size={16} /></button>
                      <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:text-red-700 p-1"><Trash2 size={16} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h3 className="text-lg font-bold text-gray-800">إنشاء فاتورة مشتريات</h3>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">المورد</label>
                <select value={supplierId} onChange={e => setSupplierId(e.target.value)} required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none">
                  <option value="">اختر مورد...</option>
                  {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">المنتجات</label>
                  <button type="button" onClick={addLine} className="flex items-center gap-1 text-indigo-600 text-sm hover:text-indigo-800">
                    <PlusCircle size={16} /><span>إضافة سطر</span>
                  </button>
                </div>
                <div className="space-y-2">
                  {lines.map((line, i) => (
                    <div key={i} className="flex gap-2 items-center">
                      <select value={line.product_id} onChange={e => handleLineProductChange(i, e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
                        <option value="">اختر منتج...</option>
                        {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                      </select>
                      <input type="number" min="1" value={line.quantity} onChange={e => updateLine(i, 'quantity', e.target.value)}
                        placeholder="الكمية" className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                      <input type="number" min="0" step="0.01" value={line.unit_price} onChange={e => updateLine(i, 'unit_price', e.target.value)}
                        placeholder="السعر" className="w-28 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                      {lines.length > 1 && (
                        <button type="button" onClick={() => removeLine(i)} className="text-red-400 hover:text-red-600"><MinusCircle size={18} /></button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <input type="checkbox" id="tax-p" checked={applyTax} onChange={e => setApplyTax(e.target.checked)} className="w-4 h-4 text-indigo-600" />
                <label htmlFor="tax-p" className="text-sm text-gray-700">تطبيق ضريبة القيمة المضافة (15%)</label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
                <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm" />
              </div>

              <div className="bg-gray-50 rounded-xl p-4 space-y-1 text-sm">
                <div className="flex justify-between"><span className="text-gray-600">الإجمالي قبل الضريبة</span><span>{subtotal.toFixed(2)} ر.س</span></div>
                <div className="flex justify-between"><span className="text-gray-600">الضريبة (15%)</span><span>{tax.toFixed(2)} ر.س</span></div>
                <div className="flex justify-between font-bold text-base border-t border-gray-200 pt-2 mt-2"><span>المجموع الكلي</span><span>{total.toFixed(2)} ر.س</span></div>
              </div>

              <div className="flex gap-3">
                <button type="submit" disabled={saving} className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg hover:bg-indigo-700 transition disabled:opacity-60">{saving ? 'جاري الحفظ...' : 'إنشاء الفاتورة'}</button>
                <button type="button" onClick={() => setShowCreate(false)} className="flex-1 bg-gray-100 text-gray-700 py-2.5 rounded-lg hover:bg-gray-200 transition">إلغاء</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {viewItem && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h3 className="text-lg font-bold text-gray-800">تفاصيل الفاتورة #{viewItem.invoice_number || viewItem.id}</h3>
              <button onClick={() => setViewItem(null)} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
            </div>
            <div className="p-6 space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div><span className="text-gray-500">المورد: </span><span className="font-medium">{suppliers.find(s => s.id === viewItem.supplier_id)?.name || viewItem.supplier_id}</span></div>
                <div><span className="text-gray-500">التاريخ: </span><span className="font-medium">{viewItem.date ? new Date(viewItem.date).toLocaleDateString('ar-SA') : '-'}</span></div>
                <div><span className="text-gray-500">الحالة: </span><span className={`px-2 py-0.5 rounded-full text-xs ${statusColor[viewItem.status] || 'bg-gray-100 text-gray-700'}`}>{statusMap[viewItem.status] || '-'}</span></div>
              </div>
              {viewItem.items && viewItem.items.length > 0 && (
                <div>
                  <p className="font-medium text-gray-700 mb-2">الأصناف:</p>
                  <table className="w-full text-xs">
                    <thead className="bg-gray-50"><tr>{['المنتج','الكمية','السعر','الإجمالي'].map(h => <th key={h} className="text-right p-2">{h}</th>)}</tr></thead>
                    <tbody className="divide-y divide-gray-50">
                      {viewItem.items.map((it, i) => (
                        <tr key={i}>
                          <td className="p-2">{products.find(p => p.id === it.product_id)?.name || it.product_id}</td>
                          <td className="p-2">{it.quantity}</td>
                          <td className="p-2">{it.unit_price}</td>
                          <td className="p-2">{(it.quantity * it.unit_price).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="bg-gray-50 rounded-xl p-3 space-y-1">
                <div className="flex justify-between"><span className="text-gray-600">الإجمالي</span><span>{(viewItem.subtotal ?? 0).toFixed(2)} ر.س</span></div>
                <div className="flex justify-between"><span className="text-gray-600">الضريبة</span><span>{(viewItem.tax_amount ?? 0).toFixed(2)} ر.س</span></div>
                <div className="flex justify-between font-bold border-t border-gray-200 pt-2"><span>المجموع</span><span>{(viewItem.total_amount ?? 0).toFixed(2)} ر.س</span></div>
              </div>
              {viewItem.notes && <p className="text-gray-600"><span className="font-medium">ملاحظات: </span>{viewItem.notes}</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
