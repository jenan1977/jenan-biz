import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { Package, Truck, Users, FileText, ShoppingCart, AlertTriangle, TrendingUp, DollarSign } from 'lucide-react'

const statCards = [
  { key: 'total_products', label: 'المنتجات', icon: Package, color: 'bg-blue-500', light: 'bg-blue-50 text-blue-700' },
  { key: 'total_suppliers', label: 'الموردين', icon: Truck, color: 'bg-purple-500', light: 'bg-purple-50 text-purple-700' },
  { key: 'total_customers', label: 'العملاء', icon: Users, color: 'bg-green-500', light: 'bg-green-50 text-green-700' },
  { key: 'total_sales_invoices', label: 'فواتير المبيعات', icon: FileText, color: 'bg-indigo-500', light: 'bg-indigo-50 text-indigo-700' },
  { key: 'total_purchase_invoices', label: 'فواتير المشتريات', icon: ShoppingCart, color: 'bg-orange-500', light: 'bg-orange-50 text-orange-700' },
  { key: 'low_stock_count', label: 'المخزون المنخفض', icon: AlertTriangle, color: 'bg-red-500', light: 'bg-red-50 text-red-700' },
  { key: 'total_revenue', label: 'الإيرادات', icon: TrendingUp, color: 'bg-teal-500', light: 'bg-teal-50 text-teal-700', currency: true },
  { key: 'total_profit', label: 'الأرباح', icon: DollarSign, color: 'bg-emerald-500', light: 'bg-emerald-50 text-emerald-700', currency: true },
]

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/dashboard/stats')
      .then(res => setStats(res.data))
      .catch(() => setStats({}))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">لوحة التحكم</h2>
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {statCards.map(({ key, label, icon: Icon, color, light, currency }) => (
            <div key={key} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex items-center gap-4">
              <div className={`${color} text-white rounded-xl p-3`}>
                <Icon size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-500">{label}</p>
                <p className="text-2xl font-bold text-gray-800">
                  {currency
                    ? `${(stats?.[key] ?? 0).toLocaleString('ar-SA', { minimumFractionDigits: 2 })} ر.س`
                    : (stats?.[key] ?? 0).toLocaleString('ar-SA')}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
