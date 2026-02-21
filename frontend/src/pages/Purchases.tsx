import React, { useEffect, useState } from 'react'
import api from '../api/axios'
import type { PurchaseInvoice, PurchaseItem, Supplier, Product } from '../types'
import { PlusIcon, EyeIcon, TrashIcon } from '@heroicons/react/24/outline'

const TAX_RATE = 0.15

interface FormState {
  supplier_id: number | ''
  date: string
  apply_tax: boolean
  notes: string
  items: PurchaseItem[]
}

const emptyForm: FormState = {
  supplier_id: '', date: new Date().toISOString().slice(0, 10),
  apply_tax: false, notes: '', items: []
}

const Purchases: React.FC = () => {
  const [invoices, setInvoices] = useState<PurchaseInvoice[]>([])
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [viewInvoice, setViewInvoice] = useState<PurchaseInvoice | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [file, setFile] = useState<File | null>(null)
  const [saving, setSaving] = useState(false)

  const fetchAll = () => {
    setLoading(true)
    Promise.all([
      api.get('/purchases/'),
      api.get('/suppliers/'),
      api.get('/products/'),
    ]).then(([inv, sup, prod]) => {
      setInvoices(inv.data)
      setSuppliers(sup.data)
      setProducts(prod.data)
    }).catch(() => setError('تعذر تحميل البيانات')).finally(() => setLoading(false))
  }
  useEffect(() => { fetchAll() }, [])

  const addItem = () => {
    setForm(f => ({ ...f, items: [...f.items, { product_id: 0, quantity: 1, unit_price: 0, total_price: 0 }] }))
  }

  const updateItem = (idx: number, field: keyof PurchaseItem, val: string | number) => {
    setForm(f => {
      const items = [...f.items]
      items[idx] = { ...items[idx], [field]: field === 'product_id' ? +val : +val }
      if (field === 'product_id') {
        const prod = products.find(p => p.id === +val)
        if (prod) items[idx].unit_price = prod.cost_price
      }
      items[idx].total_price = items[idx].quantity * items[idx].unit_price
      return { ...f, items }
    })
  }

  const removeItem = (idx: number) => setForm(f => ({ ...f, items: f.items.filter((_, i) => i !== idx) }))

  const subtotal = form.items.reduce((s, it) => s + it.total_price, 0)
  const taxAmount = form.apply_tax ? subtotal * TAX_RATE : 0
  const total = subtotal + taxAmount

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.supplier_id) { setError('يرجى اختيار المورد'); return }
    if (form.items.length === 0) { setError('يرجى إضافة منتج واحد على الأقل'); return }
    setSaving(true); setError('')
    try {
      const data = new FormData()
      data.append('supplier_id', String(form.supplier_id))
      data.append('date', form.date)
      data.append('apply_tax', String(form.apply_tax))
      data.append('notes', form.notes)
      data.append('items', JSON.stringify(form.items))
      if (file) data.append('file', file)
      await api.post('/purchases/', data, { headers: { 'Content-Type': 'multipart/form-data' } })
      setSuccess('تم إنشاء فاتورة المشتريات')
      setShowModal(false); setForm(emptyForm); setFile(null); fetchAll()
      setTimeout(() => setSuccess(''), 3000)
    } catch { setError('حدث خطأ أثناء الحفظ') }
    finally { setSaving(false) }
  }

  const inp = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500'

  return (
    <div dir="rtl" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">فواتير المشتريات</h2>
        <button onClick={() => { setForm(emptyForm); setFile(null); setShowModal(true) }}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <PlusIcon className="w-4 h-4" /> فاتورة جديدة
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
      {success && <div className="bg-green-50 border border-green-300 text-green-700 px-4 py-2 rounded-lg text-sm">{success}</div>}

      <div className="bg-white rounded-xl shadow overflow-x-auto">
        {loading ? (
          <div className="flex justify-center p-10"><svg className="animate-spin w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" /></svg></div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>{['رقم الفاتورة','المورد','التاريخ','الإجمالي','الضريبة','المجموع','الحالة','إجراءات'].map(h => <th key={h} className="px-4 py-3 text-right text-gray-600 font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? <tr><td colSpan={8} className="text-center py-8 text-gray-400">لا توجد فواتير</td></tr>
              : invoices.map(inv => (
                <tr key={inv.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{inv.invoice_number}</td>
                  <td className="px-4 py-3 text-gray-600">{inv.supplier_name || '-'}</td>
                  <td className="px-4 py-3 text-gray-600">{inv.date}</td>
                  <td className="px-4 py-3">{inv.subtotal.toFixed(2)}</td>
                  <td className="px-4 py-3">{inv.tax_amount.toFixed(2)}</td>
                  <td className="px-4 py-3 font-semibold">{inv.total_amount.toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-700">{inv.status}</span>
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => setViewInvoice(inv)} className="text-blue-600 hover:text-blue-800"><EyeIcon className="w-4 h-4" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* New Invoice Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-start justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl my-8">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">فاتورة مشتريات جديدة</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <form onSubmit={handleSave} className="p-6 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">المورد *</label>
                  <select className={inp} value={form.supplier_id} onChange={e => setForm({...form, supplier_id: +e.target.value})} required>
                    <option value="">اختر المورد</option>
                    {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">التاريخ</label>
                  <input type="date" className={inp} value={form.date} onChange={e => setForm({...form, date: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ملف (PDF/صورة)</label>
                  <input type="file" accept=".pdf,image/*" className="w-full text-sm text-gray-500 file:mr-2 file:py-1.5 file:px-3 file:rounded file:border-0 file:bg-primary-50 file:text-primary-700"
                    onChange={e => setFile(e.target.files?.[0] || null)} />
                </div>
              </div>

              {/* Items */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">المنتجات</span>
                  <button type="button" onClick={addItem} className="text-xs text-primary-600 hover:text-primary-800 flex items-center gap-1">
                    <PlusIcon className="w-3 h-3" /> إضافة منتج
                  </button>
                </div>
                <div className="space-y-2">
                  {form.items.map((item, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <select className={`flex-1 ${inp}`} value={item.product_id || ''} onChange={e => updateItem(idx, 'product_id', e.target.value)} required>
                        <option value="">اختر المنتج</option>
                        {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                      </select>
                      <input type="number" min="1" className="w-20 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="الكمية" value={item.quantity} onChange={e => updateItem(idx, 'quantity', e.target.value)} />
                      <input type="number" step="0.01" min="0" className="w-28 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="السعر" value={item.unit_price} onChange={e => updateItem(idx, 'unit_price', e.target.value)} />
                      <span className="w-24 text-sm text-gray-600 text-center">{item.total_price.toFixed(2)}</span>
                      <button type="button" onClick={() => removeItem(idx)} className="text-red-500 hover:text-red-700"><TrashIcon className="w-4 h-4" /></button>
                    </div>
                  ))}
                  {form.items.length === 0 && <p className="text-sm text-gray-400 text-center py-4">لم يتم إضافة أي منتجات بعد</p>}
                </div>
              </div>

              {/* Totals */}
              <div className="bg-gray-50 rounded-lg p-4 space-y-1 text-sm">
                <div className="flex justify-between"><span className="text-gray-600">المجموع الفرعي:</span><span>{subtotal.toFixed(2)} ر.س</span></div>
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-gray-600 cursor-pointer">
                    <input type="checkbox" checked={form.apply_tax} onChange={e => setForm({...form, apply_tax: e.target.checked})} className="w-4 h-4" />
                    تطبيق الضريبة (15%)
                  </label>
                  <span>{taxAmount.toFixed(2)} ر.س</span>
                </div>
                <div className="flex justify-between font-semibold text-gray-800 border-t pt-1"><span>الإجمالي:</span><span>{total.toFixed(2)} ر.س</span></div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
                <textarea className={inp} rows={2} value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} />
              </div>

              <div className="flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">إلغاء</button>
                <button type="submit" disabled={saving} className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm disabled:opacity-60">{saving ? 'جاري الحفظ...' : 'حفظ الفاتورة'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* View Modal */}
      {viewInvoice && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">تفاصيل الفاتورة {viewInvoice.invoice_number}</h3>
              <button onClick={() => setViewInvoice(null)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-gray-500">المورد: </span><strong>{viewInvoice.supplier_name}</strong></div>
                <div><span className="text-gray-500">التاريخ: </span><strong>{viewInvoice.date}</strong></div>
                <div><span className="text-gray-500">الحالة: </span><strong>{viewInvoice.status}</strong></div>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50"><tr>{['المنتج','الكمية','السعر','الإجمالي'].map(h => <th key={h} className="px-3 py-2 text-right text-gray-600">{h}</th>)}</tr></thead>
                <tbody>
                  {viewInvoice.items.map((it, i) => (
                    <tr key={i} className="border-t">
                      <td className="px-3 py-2">{it.product_name}</td>
                      <td className="px-3 py-2">{it.quantity}</td>
                      <td className="px-3 py-2">{it.unit_price.toFixed(2)}</td>
                      <td className="px-3 py-2">{it.total_price.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="bg-gray-50 rounded p-3 text-sm space-y-1">
                <div className="flex justify-between"><span>المجموع الفرعي</span><span>{viewInvoice.subtotal.toFixed(2)} ر.س</span></div>
                <div className="flex justify-between"><span>الضريبة</span><span>{viewInvoice.tax_amount.toFixed(2)} ر.س</span></div>
                <div className="flex justify-between font-bold border-t pt-1"><span>الإجمالي</span><span>{viewInvoice.total_amount.toFixed(2)} ر.س</span></div>
              </div>
              {viewInvoice.notes && <p className="text-sm text-gray-600">ملاحظات: {viewInvoice.notes}</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Purchases
