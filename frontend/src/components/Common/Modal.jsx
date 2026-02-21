import React, { useEffect } from 'react';

export default function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = '';
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  if (!isOpen) return null;

  const sizes = { sm: '400px', md: '600px', lg: '800px', xl: '1000px' };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 200,
      background: 'rgba(0,0,0,0.5)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: '1rem',
    }} onClick={onClose}>
      <div style={{
        background: 'var(--bg-primary)', borderRadius: 'var(--radius-xl)',
        width: '100%', maxWidth: sizes[size], maxHeight: '90vh',
        overflow: 'auto', boxShadow: 'var(--shadow-lg)',
      }} onClick={(e) => e.stopPropagation()}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-color)',
        }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>{title}</h2>
          <button onClick={onClose} style={{
            background: 'none', fontSize: '1.25rem', color: 'var(--gray-500)',
          }}>✕</button>
        </div>
        <div style={{ padding: '1.5rem' }}>{children}</div>
      </div>
    </div>
  );
}
