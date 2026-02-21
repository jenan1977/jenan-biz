import React from 'react'
import { useAuth } from '../context/AuthContext'
import { LogOut, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <h1 className="text-xl font-bold text-indigo-700">نظام جنان بيز</h1>
      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-2 text-gray-600">
            <User size={16} />
            <span className="text-sm">{user.email || user.name || 'مستخدم'}</span>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 bg-red-50 text-red-600 px-3 py-1.5 rounded-lg hover:bg-red-100 transition text-sm"
        >
          <LogOut size={16} />
          <span>تسجيل الخروج</span>
        </button>
      </div>
    </header>
  )
}
