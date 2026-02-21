import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useNotification } from '../../hooks/useNotification';

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '', full_name: '', password: '' });
  const [loading, setLoading] = useState(false);
  const notify = useNotification();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authService.register(form);
      notify.success('تم إنشاء الحساب بنجاح');
      navigate('/login');
    } catch (err) {
      notify.error(err.response?.data?.detail || 'خطأ في التسجيل');
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
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--primary-600)' }}>إنشاء حساب</h2>
        <form onSubmit={handleSubmit}>
          {[
            { name: 'full_name', label: 'الاسم الكامل', type: 'text' },
            { name: 'username', label: 'اسم المستخدم', type: 'text' },
            { name: 'email', label: 'البريد الإلكتروني', type: 'email' },
            { name: 'password', label: 'كلمة المرور', type: 'password' },
          ].map((field) => (
            <div key={field.name} className="form-group">
              <label className="form-label">{field.label}</label>
              <input
                type={field.type} name={field.name} className="form-input"
                value={form[field.name]} onChange={handleChange} required
              />
            </div>
          ))}
          <button
            type="submit" className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem', padding: '0.75rem' }}
            disabled={loading}
          >
            {loading ? 'جاري التسجيل...' : 'تسجيل'}
          </button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.875rem' }}>
          لديك حساب؟ <Link to="/login">تسجيل الدخول</Link>
        </p>
      </div>
    </div>
  );
}
