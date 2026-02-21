import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  HomeIcon,
  CubeIcon,
  TruckIcon,
  UserGroupIcon,
  ShoppingCartIcon,
  CurrencyDollarIcon,
  ClipboardDocumentListIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

const navItems = [
  { to: '/dashboard', label: 'الرئيسية', icon: HomeIcon },
  { to: '/products', label: 'المنتجات', icon: CubeIcon },
  { to: '/suppliers', label: 'الموردون', icon: TruckIcon },
  { to: '/customers', label: 'العملاء', icon: UserGroupIcon },
  { to: '/purchases', label: 'المشتريات', icon: ShoppingCartIcon },
  { to: '/sales', label: 'المبيعات', icon: CurrencyDollarIcon },
  { to: '/inventory', label: 'المخزون', icon: ClipboardDocumentListIcon },
]

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-100" dir="rtl">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-16'
        } bg-primary-900 text-white flex flex-col transition-all duration-300 ease-in-out`}
      >
        {/* Logo / Toggle */}
        <div className="flex items-center justify-between p-4 border-b border-blue-800">
          {sidebarOpen && (
            <span className="font-bold text-lg text-white">نظام الإدارة</span>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 rounded hover:bg-blue-800 text-white"
          >
            {sidebarOpen ? <XMarkIcon className="w-5 h-5" /> : <Bars3Icon className="w-5 h-5" />}
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-blue-200 hover:bg-blue-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && <span className="text-sm font-medium">{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User info at bottom */}
        {sidebarOpen && user && (
          <div className="p-4 border-t border-blue-800 text-xs text-blue-300">
            <p className="font-medium text-white truncate">{user.full_name || user.username}</p>
            <p className="truncate">{user.email}</p>
          </div>
        )}
      </aside>

      {/* Main area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm px-6 py-3 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-700">نظام إدارة الأعمال</h1>
          <div className="flex items-center gap-4">
            {user && (
              <span className="text-sm text-gray-600">
                مرحباً، <strong>{user.full_name || user.username}</strong>
              </span>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-sm text-red-600 hover:text-red-800 transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
              <span>تسجيل الخروج</span>
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  )
}

export default Layout
