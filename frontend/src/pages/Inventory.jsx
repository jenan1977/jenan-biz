import React, { useState, useEffect } from 'react'
import { getStock, getLowStock, getMovements, adjustStock } from '../services/inventoryService'
import { getProducts } from '../services/productsService'
import toast from 'react-hot-toast'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export default function Inventory() {
  const [stock, setStock] = useState([])
  const [lowStock, setLowStock] = useState([])
  const [movements, setMovements] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [adjustForm, setAdjustForm] = useState({ product_id: '', quantity: '', reason: '' })
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('stock')

  const load = () => {
    setLoading(true)
    Promise.all([getStock(), getLowStock(), getMovements(), getProducts()])
      .then(([s, ls, mv, pr]) => { setStock(s.data); setLowStock(ls.data); setMovements(mv.data); setProducts(pr.data) })
      .catch(() => toast.error('خطأ في تحميل بيانات المخزون'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleAdjust = async (e) => {
    e.preventDefault(); setSaving(true)
    try {
      await adjustStock({ product_id: Number(adjustForm.product_id), quantity: Number(adjustForm.quantity), reason: adjustForm.reason })
      toast.success('تم تعديل المخزون')
      setAdjustForm({ product_id: '', quantity: '', reason: '' })
      load()
    } catch { toast.error('خطأ في تعديل المخزون') } finally { setSaving(false) }
  }

  const getProductName = (id) => products.find(p => p.id === id)?.name || `#${id}`

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">المخزون</h2>
        <button onClick={load} className="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 text-sm">
          <RefreshCw size={16} /><span>تحديث</span>
        </button>
      </div>

      {lowStock.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
          <AlertTriangle className="text-red-500 mt-0.5" size={20} />
          <div>
            <p className="font-semibold text-red-700">تنبيه: مخزون منخفض</p>
            <p className="text-red-600 text-sm mt-1">
              {lowStock.length} منتج/منتجات تحتاج إلى إعادة تخزين: {lowStock.map(i => getProductName(i.product_id || i.id)).join('، ')}
            </p>
          </div>
        </div>
      )}

      <div className="flex gap-1 mb-4 bg-gray-100 p-1 rounded-xl w-fit">
        {[
          { key: 'stock', label: 'مستويات المخزون' },
          { key: 'movements', label: 'حركات المخزون' },
          { key: 'adjust', label: 'تعديل يدوي' },
        ].map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${activeTab === tab.key ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-600 hover:text-gray-800'}`}>
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div></div>
      ) : (
        <>
          {activeTab === 'stock' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    {['المنتج','الكمية الحالية','الحد الأدنى','الحالة'].map(h => (
                      <th key={h} className="text-right px-4 py-3 text-gray-600 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {stock.length === 0 ? (
                    <tr><td colSpan={4} className="text-center py-10 text-gray-400">لا توجد بيانات مخزون</td></tr>
                  ) : stock.map((item, i) => {
                    const prod = products.find(p => p.id === (item.product_id || item.id))
                    const isLow = item.quantity <= (prod?.min_stock ?? 0)
                    return (
                      <tr key={i} className="hover:bg-gray-50 transition">
                        <td className="px-4 py-3 font-medium text-gray-800">{getProductName(item.product_id || item.id)}</td>
                        <td className="px-4 py-3 text-gray-700">{item.quantity}</td>
                        <td className="px-4 py-3 text-gray-600">{prod?.min_stock ?? '-'}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${isLow ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                            {isLow ? 'منخفض' : 'طبيعي'}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'movements' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    {['المنتج','النوع','الكمية','التاريخ','السبب'].map(h => (
                      <th key={h} className="text-right px-4 py-3 text-gray-600 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {movements.length === 0 ? (
                    <tr><td colSpan={5} className="text-center py-10 text-gray-400">لا توجد حركات مخزون</td></tr>
                  ) : movements.map((mv, i) => (
                    <tr key={i} className="hover:bg-gray-50 transition">
                      <td className="px-4 py-3 font-medium text-gray-800">{getProductName(mv.product_id)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${mv.type === 'in' || mv.movement_type === 'in' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {(mv.type === 'in' || mv.movement_type === 'in') ? 'وارد' : 'صادر'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-700">{mv.quantity}</td>
                      <td className="px-4 py-3 text-gray-600">{mv.date || mv.created_at ? new Date(mv.date || mv.created_at).toLocaleDateString('ar-SA') : '-'}</td>
                      <td className="px-4 py-3 text-gray-600">{mv.reason || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'adjust' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 max-w-md">
              <h3 className="font-semibold text-gray-800 mb-4">تعديل المخزون يدوياً</h3>
              <form onSubmit={handleAdjust} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">المنتج</label>
                  <select value={adjustForm.product_id} onChange={e => setAdjustForm(f => ({ ...f, product_id: e.target.value }))} required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm">
                    <option value="">اختر منتج...</option>
                    {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الكمية (موجب للإضافة، سالب للخصم)</label>
                  <input type="number" value={adjustForm.quantity} onChange={e => setAdjustForm(f => ({ ...f, quantity: e.target.value }))} required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="مثال: 10 أو -5" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">السبب</label>
                  <input type="text" value={adjustForm.reason} onChange={e => setAdjustForm(f => ({ ...f, reason: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="سبب التعديل" />
                </div>
                <button type="submit" disabled={saving} className="w-full bg-indigo-600 text-white py-2.5 rounded-lg hover:bg-indigo-700 transition disabled:opacity-60 text-sm font-medium">
                  {saving ? 'جاري التعديل...' : 'تطبيق التعديل'}
                </button>
              </form>
            </div>
          )}
        </>
      )}
    </div>
  )
}
