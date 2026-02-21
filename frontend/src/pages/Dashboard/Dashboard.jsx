import React, { useEffect, useState } from 'react';
import { useCompany } from '../../hooks/useCompany';
import { reportsService } from '../../services/reportsService';
import { format } from 'date-fns';

function StatCard({ icon, label, value, color }) {
  return (
    <div className="stat-card">
      <div style={{
        fontSize: '2rem', width: 56, height: 56, borderRadius: 'var(--radius-lg)',
        background: color + '20', display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>{icon}</div>
      <div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{label}</div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color }}>{value}</div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { currentCompany } = useCompany();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (!currentCompany?.id) return;
    const today = format(new Date(), 'yyyy-MM-dd');
    const firstDay = format(new Date(new Date().getFullYear(), new Date().getMonth(), 1), 'yyyy-MM-dd');
    reportsService.profit(currentCompany.id, firstDay, today)
      .then((res) => setStats(res.data))
      .catch(console.error);
  }, [currentCompany]);

  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>
        لوحة التحكم
      </h1>
      <div className="stats-grid">
        <StatCard icon="💰" label="إجمالي المبيعات (هذا الشهر)" value={`${stats?.total_sales?.toFixed(2) || 0} ر.س`} color="var(--success)" />
        <StatCard icon="🛒" label="إجمالي المشتريات" value={`${stats?.total_purchases?.toFixed(2) || 0} ر.س`} color="var(--info)" />
        <StatCard icon="📈" label="الربح الإجمالي" value={`${stats?.gross_profit?.toFixed(2) || 0} ر.س`} color="var(--primary-600)" />
        <StatCard icon="%" label="هامش الربح" value={`${stats?.profit_margin_percent || 0}%`} color="var(--warning)" />
      </div>
      <div className="card">
        <h2 style={{ marginBottom: '1rem' }}>مرحباً بك في نظام جنان بيز</h2>
        <p style={{ color: 'var(--text-secondary)' }}>نظام محاسبي ذكي متكامل لإدارة أعمالك بكفاءة واحترافية</p>
      </div>
    </div>
  );
}
