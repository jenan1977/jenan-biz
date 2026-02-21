import React, { useEffect, useState } from 'react'
import api from '../api/axios'
import type { DashboardSummary } from '../types'
import {
  CurrencyDollarIcon,
  ShoppingCartIcon,
  CubeIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get('/dashboard/summary')
      .then((res) => setSummary(res.data))
      .catch(() => setError('تعذر تحميل بيانات لوحة التحكم'))
      .finally(() => setLoading(false))
  }, [])

  if (loading)
    return (
      <div className="flex justify-center items-center h-64">
        <svg className="animate-spin w-10 h-10 text-primary-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
      </div>
    )

  if (error)
    return (
      <div className="bg-red-50 border border-red-300 text-red-700 p-4 rounded-lg">{error}</div>
    )

  const cards = [
    {
      label: 'مبيعات اليوم',
      value: `${summary?.today_sales?.toFixed(2) || '0.00'} ر.س`,
      sub: `${summary?.today_sales_count || 0} فاتورة`,
      icon: CurrencyDollarIcon,
      color: 'bg-green-500',
    },
    {
      label: 'مشتريات اليوم',
      value: `${summary?.today_purchases?.toFixed(2) || '0.00'} ر.س`,
      sub: `${summary?.today_purchases_count || 0} فاتورة`,
      icon: ShoppingCartIcon,
      color: 'bg-blue-500',
    },
    {
      label: 'إجمالي المنتجات',
      value: summary?.total_products || 0,
      sub: 'منتج نشط',
      icon: CubeIcon,
      color: 'bg-purple-500',
    },
    {
      label: 'منتجات منخفضة المخزون',
      value: summary?.low_stock_count || 0,
      sub: 'تحتاج إعادة تعبئة',
      icon: ExclamationTriangleIcon,
      color: 'bg-red-500',
    },
  ]

  const chartData = {
    labels: ['مبيعات اليوم', 'مشتريات اليوم'],
    datasets: [
      {
        label: 'المبلغ (ر.س)',
        data: [summary?.today_sales || 0, summary?.today_purchases || 0],
        backgroundColor: ['rgba(34,197,94,0.7)', 'rgba(59,130,246,0.7)'],
        borderColor: ['#16a34a', '#2563eb'],
        borderWidth: 1,
      },
    ],
  }

  return (
    <div dir="rtl" className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">لوحة التحكم</h2>

      {/* Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div key={card.label} className="bg-white rounded-xl shadow p-5 flex items-center gap-4">
            <div className={`${card.color} p-3 rounded-lg`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{card.label}</p>
              <p className="text-xl font-bold text-gray-800">{card.value}</p>
              <p className="text-xs text-gray-400">{card.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">ملخص اليوم</h3>
        <div className="max-w-md">
          <Bar
            data={chartData}
            options={{
              responsive: true,
              plugins: { legend: { position: 'top' } },
            }}
          />
        </div>
      </div>

      {/* Recent Transactions */}
      {summary?.recent_transactions && summary.recent_transactions.length > 0 && (
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">آخر المعاملات</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-right text-gray-600">رقم الفاتورة</th>
                  <th className="px-4 py-2 text-right text-gray-600">النوع</th>
                  <th className="px-4 py-2 text-right text-gray-600">المبلغ</th>
                  <th className="px-4 py-2 text-right text-gray-600">التاريخ</th>
                </tr>
              </thead>
              <tbody>
                {summary.recent_transactions.map((tx: any, idx: number) => (
                  <tr key={idx} className="border-t border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-2">{tx.invoice_number || '-'}</td>
                    <td className="px-4 py-2">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${
                          tx.type === 'sale'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}
                      >
                        {tx.type === 'sale' ? 'مبيعة' : 'مشترى'}
                      </span>
                    </td>
                    <td className="px-4 py-2">{tx.total_amount?.toFixed(2)} ر.س</td>
                    <td className="px-4 py-2">{tx.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
