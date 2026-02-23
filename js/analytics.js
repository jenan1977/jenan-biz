/**
 * analytics.js - Business analytics page logic.
 *
 * Flow:
 *  1. POST /api/v1/agents/analyze  → get job_id
 *  2. Poll GET /api/v1/agents/jobs/{job_id} until SUCCEEDED/FAILED
 *  3. Render the result in the page
 */

const API_BASE = window.API_BASE_URL || '';
const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 30;

function setStatus(msg, type = 'info') {
    const el = document.getElementById('status-msg');
    el.className = type;
    el.innerHTML = (type === 'info' ? '<span class="spinner"></span>' : '') + msg;
}

function clearStatus() {
    const el = document.getElementById('status-msg');
    el.className = 'success';
    el.textContent = '';
}

function fmt(val) {
    return Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

async function pollJob(jobId, token) {
    for (let i = 0; i < MAX_POLL_ATTEMPTS; i++) {
        await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
        const resp = await fetch(`${API_BASE}/api/v1/agents/jobs/${jobId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!resp.ok) {
            throw new Error(`Poll failed: ${resp.status} ${resp.statusText}`);
        }
        const data = await resp.json();
        if (data.status === 'SUCCEEDED') return data.result;
        if (data.status === 'FAILED')   throw new Error(`Job failed: ${data.error || 'unknown error'}`);
        setStatus(`Processing… (attempt ${i + 1}/${MAX_POLL_ATTEMPTS})`);
    }
    throw new Error('Timed out waiting for analytics job to complete.');
}

async function loadAnalytics() {
    const companyId = document.getElementById('company-id').value.trim();
    const fromDate  = document.getElementById('from-date').value;
    const toDate    = document.getElementById('to-date').value;
    const token     = document.getElementById('jwt-token').value.trim();

    if (!companyId || !fromDate || !toDate || !token) {
        setStatus('Please fill in all fields (Company ID, From, To, JWT Token).', 'error');
        return;
    }

    document.getElementById('load-btn').disabled = true;
    setStatus('Submitting analytics job…');

    try {
        // 1. Enqueue
        const resp = await fetch(`${API_BASE}/api/v1/agents/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ company_id: companyId, from_date: fromDate, to_date: toDate }),
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${resp.status}`);
        }

        const { job_id } = await resp.json();
        setStatus(`Job ${job_id} queued. Waiting for results…`);

        // 2. Poll
        const result = await pollJob(job_id, token);

        // 3. Render
        document.getElementById('total-sales').textContent     = fmt(result.total_sales);
        document.getElementById('total-purchases').textContent = fmt(result.total_purchases);
        document.getElementById('low-stock-count').textContent = result.low_stock_alerts.length;
        document.getElementById('top-customers-count').textContent = result.top_customers.length;

        const custBody = document.getElementById('top-customers-body');
        if (result.top_customers.length === 0) {
            custBody.innerHTML = '<tr><td colspan="3" style="color:#aaa">No sales in this period.</td></tr>';
        } else {
            custBody.innerHTML = result.top_customers
                .map((c, i) => `<tr><td>${i + 1}</td><td>${escHtml(c.name)}</td><td>${fmt(c.total)}</td></tr>`)
                .join('');
        }

        const stockBody = document.getElementById('low-stock-body');
        if (result.low_stock_alerts.length === 0) {
            stockBody.innerHTML = '<tr><td colspan="3" style="color:#aaa">All products are well-stocked.</td></tr>';
        } else {
            stockBody.innerHTML = result.low_stock_alerts
                .map(p =>
                    `<tr>
                        <td>${escHtml(p.name)}</td>
                        <td>${fmt(p.available)}</td>
                        <td><span class="alert-badge">Low Stock</span></td>
                    </tr>`
                )
                .join('');
        }

        clearStatus();
    } catch (err) {
        setStatus(`Error: ${err.message}`, 'error');
    } finally {
        document.getElementById('load-btn').disabled = false;
    }
}

function escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
