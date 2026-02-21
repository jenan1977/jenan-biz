import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { companiesService } from '../../services/companiesService';
import { setCurrentCompany } from '../../store/companySlice';
import { useNotification } from '../../hooks/useNotification';

const BUSINESS_TYPES = [
  { value: 'retail', label: '🛍️ تجزئة' },
  { value: 'wholesale', label: '🏭 جملة' },
  { value: 'restaurant', label: '🍽️ مطعم' },
  { value: 'pharmacy', label: '💊 صيدلية' },
  { value: 'services', label: '🔧 خدمات' },
  { value: 'other', label: '📋 أخرى' },
];

export default function BusinessSetup() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ name: '', business_type: '', country: 'Saudi Arabia', currency: 'SAR', vat_rate: 15 });
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const notify = useNotification();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await companiesService.create(form);
      dispatch(setCurrentCompany(res.data));
      notify.success('تم إنشاء الشركة بنجاح!');
      navigate('/dashboard');
    } catch (err) {
      notify.error(err.response?.data?.detail || 'خطأ في إنشاء الشركة');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-secondary)',
    }}>
      <div className="card" style={{ width: '100%', maxWidth: '600px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--primary-600)' }}>
          إعداد شركتك
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">اسم الشركة *</label>
            <input className="form-input" name="name" value={form.name} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label className="form-label">نوع النشاط التجاري</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', marginTop: '0.5rem' }}>
              {BUSINESS_TYPES.map((type) => (
                <button
                  key={type.value} type="button"
                  onClick={() => setForm({ ...form, business_type: type.value })}
                  style={{
                    padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '2px solid',
                    borderColor: form.business_type === type.value ? 'var(--primary-500)' : 'var(--border-color)',
                    background: form.business_type === type.value ? 'var(--primary-50)' : 'transparent',
                    cursor: 'pointer', fontSize: '0.875rem',
                  }}
                >
                  {type.label}
                </button>
              ))}
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">العملة</label>
              <select className="form-input" name="currency" value={form.currency} onChange={handleChange}>
                <option value="SAR">ريال سعودي (SAR)</option>
                <option value="USD">دولار (USD)</option>
                <option value="EUR">يورو (EUR)</option>
                <option value="AED">درهم (AED)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">نسبة ضريبة القيمة المضافة (%)</label>
              <input className="form-input" type="number" name="vat_rate" value={form.vat_rate} onChange={handleChange} min={0} max={100} />
            </div>
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.75rem', marginTop: '1rem' }} disabled={loading}>
            {loading ? 'جاري الإنشاء...' : 'إنشاء الشركة والمتابعة →'}
          </button>
        </form>
      </div>
    </div>
  );
}
