import React, { useEffect, useState } from 'react'
import api from '../api/axios'
import type { Supplier } from '../types'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'

const empty: Omit<Supplier, 'id'> = { name: '', contact_person: '', phone: '', email: '', address: '', tax_number: '', is_active: true }

const Suppliers: React.FC = () => {
  const [items, setItems] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Supplier | null>(null)
  const [form, setForm] = useState<Omit<Supplier, 'id'>>(empty)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [saving, setSaving] = useState(false)

  const fetch = () => {
    setLoading(true)
    api.get('/suppliers/').then(r => setItems(r.data)).catch(() => setError('تعذر تحميل الموردين')).finally(() => setLoading(false))
  }
  useEffect(() => { fetch() }, [])

  const openAdd = () => { setEditing(null); setForm(empty); setShowModal(true) }
  const openEdit = (s: Supplier) => { setEditing(s); setForm({ name: s.name, contact_person: s.contact_person||'', phone: s.phone||'', email: s.email||'', address: s.address||'', tax_number: s.tax_number||'', is_active: s.is_active }); setShowModal(true) }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) { setError('الاسم مطلوب'); return }
    setSaving(true); setError('')
    try {
      if (editing) await api.put(`/suppliers/${editing.id}`, form)
      else await api.post('/suppliers/', form)
      setSuccess(editing ? 'تم تحديث المورد' : 'تم إضافة المورد')
      setShowModal(false); fetch(); setTimeout(() => setSuccess(''), 3000)
    } catch { setError('حدث خطأ أثناء الحفظ') }
    finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    try { await api.delete(`/suppliers/${deleteId}`); setSuccess('تم حذف المورد'); setDeleteId(null); fetch(); setTimeout(() => setSuccess(''), 3000) }
    catch { setError('تعذر حذف المورد') }
  }

  const inp = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500'

  return (
    <div dir="rtl" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">الموردون</h2>
        <button onClick={openAdd} className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
          <PlusIcon className="w-4 h-4" /> إضافة مورد
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
      {success && <div className="bg-green-50 border border-green-300 text-green-700 px-4 py-2 rounded-lg text-sm">{success}</div>}

      <div className="bg-white rounded-xl shadow overflow-x-auto">
        {loading ? (
          <div className="flex justify-center p-10"><svg className="animate-spin w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" /></svg></div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>{['الاسم','جهة الاتصال','الهاتف','البريد','العنوان','الحالة','إجراءات'].map(h => <th key={h} className="px-4 py-3 text-right text-gray-600 font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {items.length === 0 ? <tr><td colSpan={7} className="text-center py-8 text-gray-400">لا يوجد موردون</td></tr>
              : items.map(s => (
                <tr key={s.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{s.name}</td>
                  <td className="px-4 py-3 text-gray-500">{s.contact_person || '-'}</td>
                  <td className="px-4 py-3 text-gray-500">{s.phone || '-'}</td>
                  <td className="px-4 py-3 text-gray-500">{s.email || '-'}</td>
                  <td className="px-4 py-3 text-gray-500">{s.address || '-'}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs ${s.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>{s.is_active ? 'نشط' : 'غير نشط'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => openEdit(s)} className="text-blue-600 hover:text-blue-800"><PencilIcon className="w-4 h-4" /></button>
                      <button onClick={() => setDeleteId(s.id)} className="text-red-500 hover:text-red-700"><TrashIcon className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">{editing ? 'تعديل المورد' : 'إضافة مورد'}</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <form onSubmit={handleSave} className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">الاسم *</label><input className={inp} value={form.name} onChange={e => setForm({...form, name: e.target.value})} required /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">جهة الاتصال</label><input className={inp} value={form.contact_person} onChange={e => setForm({...form, contact_person: e.target.value})} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">الهاتف</label><input className={inp} value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label><input type="email" className={inp} value={form.email} onChange={e => setForm({...form, email: e.target.value})} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">الرقم الضريبي</label><input className={inp} value={form.tax_number} onChange={e => setForm({...form, tax_number: e.target.value})} /></div>
              <div className="sm:col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">العنوان</label><textarea className={inp} rows={2} value={form.address} onChange={e => setForm({...form, address: e.target.value})} /></div>
              <div className="sm:col-span-2 flex items-center gap-2"><input type="checkbox" id="sup_active" checked={form.is_active} onChange={e => setForm({...form, is_active: e.target.checked})} className="w-4 h-4" /><label htmlFor="sup_active" className="text-sm text-gray-700">نشط</label></div>
              <div className="sm:col-span-2 flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">إلغاء</button>
                <button type="submit" disabled={saving} className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm disabled:opacity-60">{saving ? 'جاري الحفظ...' : 'حفظ'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold mb-3">تأكيد الحذف</h3>
            <p className="text-gray-600 text-sm mb-5">هل أنت متأكد من حذف هذا المورد؟</p>
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

export default Suppliers
