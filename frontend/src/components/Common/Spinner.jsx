import React from 'react';

export default function Spinner({ size = 'md', center = false }) {
  const sizes = { sm: 20, md: 40, lg: 60 };
  const px = sizes[size] || 40;

  return (
    <div style={{
      display: 'flex', justifyContent: center ? 'center' : 'flex-start',
      alignItems: 'center', padding: center ? '2rem' : '0',
    }}>
      <div style={{
        width: px, height: px,
        border: `${px / 10}px solid var(--gray-200)`,
        borderTopColor: 'var(--primary-500)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
