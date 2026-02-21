import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useNotification } from '../../hooks/useNotification';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const notify = useNotification();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      notify.success('تم تسجيل الدخول بنجاح');
      navigate('/dashboard');
    } catch (err) {
      notify.error(err.response?.data?.detail || 'خطأ في تسجيل الدخول');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--primary-600)' }}>جنان بيز</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>نظام محاسبي ذكي</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">البريد الإلكتروني</label>
            <input
              type="email" className="form-input"
              value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="example@company.com" required
            />
          </div>
          <div className="form-group">
            <label className="form-label">كلمة المرور</label>
            <input
              type="password" className="form-input"
              value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••" required
            />
          </div>
          <button
            type="submit" className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem', padding: '0.75rem' }}
            disabled={loading}
          >
            {loading ? 'جاري الدخول...' : 'تسجيل الدخول'}
          </button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.875rem' }}>
          ليس لديك حساب؟ <Link to="/register">سجل الآن</Link>
        </p>
      </div>
    </div>
  );
}
