import React from 'react';
import { NavLink } from 'react-router-dom';

const menuItems = [
  { path: '/dashboard', label: 'لوحة التحكم', icon: '📊' },
  { path: '/products', label: 'المنتجات', icon: '📦' },
  { path: '/inventory', label: 'المخزون', icon: '🏭' },
  { path: '/purchases', label: 'المشتريات', icon: '🛒' },
  { path: '/sales', label: 'المبيعات', icon: '💰' },
  { path: '/customers', label: 'العملاء', icon: '👥' },
  { path: '/suppliers', label: 'الموردون', icon: '🏢' },
  { path: '/reports', label: 'التقارير', icon: '📈' },
  { path: '/analytics', label: 'التحليلات', icon: '🔍' },
  { path: '/settings', label: 'الإعدادات', icon: '⚙️' },
];

export default function Sidebar({ isOpen }) {
  return (
    <aside style={{
      position: 'fixed', top: 'var(--navbar-height)', right: 0, bottom: 0,
      width: 'var(--sidebar-width)',
      background: 'var(--bg-primary)',
      borderLeft: '1px solid var(--border-color)',
      overflowY: 'auto', zIndex: 90,
      transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
      transition: 'transform 0.3s ease',
    }}>
      <div style={{ padding: '1rem' }}>
        <div style={{
          fontWeight: 700, fontSize: '1.25rem', color: 'var(--primary-600)',
          padding: '1rem 0.5rem', borderBottom: '1px solid var(--border-color)',
          marginBottom: '0.5rem',
        }}>
          جنان بيز 📱
        </div>
        <nav>
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: '0.75rem',
                padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)',
                color: isActive ? 'var(--primary-600)' : 'var(--text-secondary)',
                background: isActive ? 'var(--primary-50)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                fontSize: '0.9rem', marginBottom: '0.25rem',
                transition: 'all 0.2s',
              })}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  );
}
