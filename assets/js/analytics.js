/**
 * analytics.js – Client-side logic for the Jenan-Biz Analytics Dashboard.
 *
 * Communicates with the Agents API served from the same origin.
 * All API calls go to /api/v1/agents/…
 */

'use strict';

const Analytics = (() => {
  const API_BASE = '/api/v1/agents';
  const POLL_INTERVAL_MS = 2000;
  const MAX_POLL_ATTEMPTS = 60; // 2 min total

  // ── Toast notifications ───────────────────────────────────────────────
  function toast(msg, type = 'info') {
    const bar = document.getElementById('status-bar');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = msg;
    bar.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }

  // ── Build date payload from form ──────────────────────────────────────
  function getDatePayload() {
    const from = document.getElementById('date-from').value;
    const to   = document.getElementById('date-to').value;
    const payload = {};
    if (from) payload.date_from = from;
    if (to)   payload.date_to   = to;
    return payload;
  }

  // ── Generic POST to enqueue a job ─────────────────────────────────────
  async function enqueueJob(endpoint, payload) {
    const resp = await fetch(`${API_BASE}/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(err.detail || resp.statusText);
    }
    return resp.json();
  }

  // ── Poll job until finished ───────────────────────────────────────────
  async function pollJob(jobId) {
    showJobPoller(jobId);
    let attempts = 0;

    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        attempts++;
        const pct = Math.min(95, (attempts / MAX_POLL_ATTEMPTS) * 100);
        document.getElementById('job-progress-bar').style.width = `${pct}%`;

        try {
          const resp = await fetch(`${API_BASE}/jobs/${jobId}`);
          if (!resp.ok) throw new Error(resp.statusText);
          const job = await resp.json();

          document.getElementById('job-status-text').textContent =
            `جارٍ المعالجة… (${job.status})`;

          if (job.status === 'succeeded') {
            clearInterval(interval);
            document.getElementById('job-progress-bar').style.width = '100%';
            hideJobPoller();
            resolve(job);
          } else if (job.status === 'failed') {
            clearInterval(interval);
            hideJobPoller();
            reject(new Error(job.error || 'Job failed'));
          } else if (attempts >= MAX_POLL_ATTEMPTS) {
            clearInterval(interval);
            hideJobPoller();
            reject(new Error('Job timed out'));
          }
        } catch (err) {
          clearInterval(interval);
          hideJobPoller();
          reject(err);
        }
      }, POLL_INTERVAL_MS);
    });
  }

  function showJobPoller(jobId) {
    const el = document.getElementById('job-poller');
    el.style.display = 'block';
    document.getElementById('job-status-text').textContent = `Job ${jobId} – جارٍ الانتظار…`;
    document.getElementById('job-progress-bar').style.width = '5%';
  }

  function hideJobPoller() {
    document.getElementById('job-poller').style.display = 'none';
  }

  // ── Render results ────────────────────────────────────────────────────
  function renderAnalysis(result) {
    document.getElementById('kpi-sales').textContent =
      formatMoney(result.total_sales);
    document.getElementById('kpi-purchases').textContent =
      formatMoney(result.total_purchases);
    document.getElementById('kpi-low-stock').textContent =
      result.low_stock_alerts.length;

    // Top customers
    const tbody = document.getElementById('tbl-customers');
    tbody.innerHTML = '';
    result.top_customers.forEach((c, i) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td>${escHtml(c.customer_name || c.customer_id)}</td>
        <td>${formatMoney(c.total_spend)}</td>`;
      tbody.appendChild(tr);
    });
    document.getElementById('section-customers').style.display =
      result.top_customers.length ? '' : 'none';

    // Low stock
    const tbody2 = document.getElementById('tbl-lowstock');
    tbody2.innerHTML = '';
    result.low_stock_alerts.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escHtml(item.inventory_id)}</td>
        <td>${item.quantity_available}</td>
        <td>${item.reorder_level}</td>`;
      tbody2.appendChild(tr);
    });
    document.getElementById('section-lowstock').style.display =
      result.low_stock_alerts.length ? '' : 'none';
  }

  // ── Public actions ────────────────────────────────────────────────────
  async function runAnalysis() {
    const btn = document.getElementById('btn-analyze');
    btn.disabled = true;
    try {
      toast('جارٍ تحليل البيانات…');
      const { job_id } = await enqueueJob('analyze', getDatePayload());
      const job = await pollJob(job_id);
      renderAnalysis(job.result);
      toast('اكتمل التحليل بنجاح', 'success');
    } catch (err) {
      toast(`خطأ: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
    }
  }

  async function generateReport() {
    const btn = document.getElementById('btn-report');
    btn.disabled = true;
    try {
      toast('جارٍ إنشاء التقرير…');
      const { job_id } = await enqueueJob('report', getDatePayload());
      await pollJob(job_id);
      // Trigger download
      window.location.href = `${API_BASE}/jobs/${job_id}/download`;
      toast('تم إنشاء التقرير بنجاح', 'success');
    } catch (err) {
      toast(`خطأ: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────
  function formatMoney(value) {
    const num = parseFloat(value) || 0;
    return num.toLocaleString('ar-SA', { style: 'currency', currency: 'SAR' });
  }

  function escHtml(str) {
    const d = document.createElement('div');
    d.textContent = str ?? '';
    return d.innerHTML;
  }

  return { runAnalysis, generateReport };
})();
