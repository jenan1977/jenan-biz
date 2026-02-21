import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setTheme } from '../../store/settingsSlice';
import { useAuth } from '../../hooks/useAuth';

export default function Navbar({ onMenuToggle }) {
  const dispatch = useDispatch();
  const { user, logout } = useAuth();
  const { theme, currentCompany } = useSelector((state) => ({
    theme: state.settings.theme,
    currentCompany: state.company.currentCompany,
  }));

  const toggleTheme = () => dispatch(setTheme(theme === 'light' ? 'dark' : 'light'));

  return (
    <nav className="navbar" style={{
      position: 'fixed', top: 0, right: 0, left: 0,
      height: 'var(--navbar-height)', background: 'var(--bg-primary)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', padding: '0 1.5rem', zIndex: 100,
      boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button onClick={onMenuToggle} style={{ background: 'none', fontSize: '1.25rem' }}>☰</button>
        {currentCompany && (
          <span style={{ fontWeight: 600, color: 'var(--primary-600)' }}>
            {currentCompany.name}
          </span>
        )}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button onClick={toggleTheme} style={{ background: 'none', fontSize: '1.1rem' }}>
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          {user?.full_name}
        </span>
        <button className="btn btn-secondary" onClick={logout} style={{ fontSize: '0.8rem' }}>
          تسجيل الخروج
        </button>
      </div>
    </nav>
  );
}
