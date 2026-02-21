import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Package,
  Truck,
  Users,
  ShoppingCart,
  FileText,
  Warehouse
} from 'lucide-react'

const navItems = [
  { to: '/', label: 'الرئيسية', icon: LayoutDashboard, end: true },
  { to: '/products', label: 'المنتجات', icon: Package },
  { to: '/suppliers', label: 'الموردين', icon: Truck },
  { to: '/customers', label: 'العملاء', icon: Users },
  { to: '/purchases', label: 'المشتريات', icon: ShoppingCart },
  { to: '/sales', label: 'المبيعات', icon: FileText },
  { to: '/inventory', label: 'المخزون', icon: Warehouse },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-indigo-900 text-white flex flex-col shadow-xl">
      <div className="p-4 border-b border-indigo-700">
        <p className="text-xs text-indigo-300 text-center">القائمة الرئيسية</p>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-lg transition text-sm ${
                isActive
                  ? 'bg-indigo-600 text-white font-semibold'
                  : 'text-indigo-200 hover:bg-indigo-800'
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
