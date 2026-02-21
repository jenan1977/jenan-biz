# jenan-biz — نظام إدارة الأعمال

منصة تجارية احترافية متكاملة لإدارة المشتريات والمبيعات والمخزون والمنتجات.

## 🚀 التشغيل السريع (Docker)

```bash
git clone https://github.com/jenan1977/jenan-biz.git
cd jenan-biz
docker compose up --build
```

افتح المتصفح على: **http://localhost:3000**

بيانات الدخول الافتراضية:
- اسم المستخدم: `admin`
- كلمة المرور: `admin123`

> ملاحظة: يتم إنشاء حساب المشرف تلقائياً عند أول تشغيل.

---

## 📦 المتطلبات

- Docker + Docker Compose

أو للتشغيل المحلي:
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

---

## 🏗️ البنية التقنية

```
jenan-biz/
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL
├── frontend/         # React 18 + TypeScript + Tailwind CSS
└── docker-compose.yml
```

---

## 🖥️ Backend (FastAPI)

### التشغيل المحلي

```bash
cd backend
pip install -r requirements.txt
# ضبط متغيرات البيئة
export DATABASE_URL=postgresql://jenan:jenanpass@localhost:5432/jenan_biz
export SECRET_KEY=your-secret-key
uvicorn app.main:app --reload
```

التوثيق التفاعلي: **http://localhost:8000/docs**

### نقاط النهاية (API Endpoints)

| الوحدة | المسار | الوصف |
|--------|--------|-------|
| المصادقة | `POST /api/v1/auth/login` | تسجيل الدخول |
| المصادقة | `POST /api/v1/auth/register` | إنشاء مستخدم |
| المصادقة | `GET /api/v1/auth/me` | معلومات المستخدم |
| المنتجات | `GET/POST /api/v1/products` | قائمة وإضافة |
| المنتجات | `GET/PUT/DELETE /api/v1/products/{id}` | تعديل وحذف |
| المنتجات | `GET /api/v1/products/low-stock` | منتجات منخفضة المخزون |
| الموردون | `GET/POST /api/v1/suppliers` | قائمة وإضافة |
| الموردون | `GET/PUT/DELETE /api/v1/suppliers/{id}` | تعديل وحذف |
| العملاء | `GET/POST /api/v1/customers` | قائمة وإضافة |
| العملاء | `GET/PUT/DELETE /api/v1/customers/{id}` | تعديل وحذف |
| المشتريات | `GET/POST /api/v1/purchases` | قائمة وإنشاء فاتورة |
| المشتريات | `GET /api/v1/purchases/{id}` | تفاصيل الفاتورة |
| المشتريات | `POST /api/v1/purchases/{id}/upload-file` | رفع ملف |
| المبيعات | `GET/POST /api/v1/sales` | قائمة وإنشاء فاتورة |
| المبيعات | `GET /api/v1/sales/{id}` | تفاصيل الفاتورة |
| المبيعات | `GET /api/v1/sales/{id}/pdf` | تحميل PDF |
| المخزون | `GET /api/v1/inventory/movements` | حركات المخزون |
| المخزون | `GET /api/v1/inventory/stock-report` | تقرير المخزون |
| المخزون | `POST /api/v1/inventory/adjustment` | تعديل يدوي |
| لوحة التحكم | `GET /api/v1/dashboard/summary` | ملخص عام |

---

## 🎨 Frontend (React)

### التشغيل المحلي

```bash
cd frontend
npm install
npm run dev
```

التطبيق: **http://localhost:5173**

### الصفحات

- **لوحة التحكم** — ملخص اليوم، آخر المعاملات، مخطط بياني
- **المنتجات** — إضافة/تعديل/حذف المنتجات مع إدارة الأسعار
- **الموردون** — إدارة قائمة الموردين
- **العملاء** — إدارة قائمة العملاء
- **المشتريات** — إنشاء فواتير الشراء مع رفع الملفات
- **المبيعات** — إنشاء فواتير المبيعات وتحميل PDF
- **المخزون** — تقرير المخزون، الحركات، التعديلات اليدوية

---

## 🗄️ قاعدة البيانات

### Migrations

```bash
cd backend
alembic upgrade head
```

### الجداول الرئيسية

- `users` — المستخدمون والصلاحيات
- `products` — المنتجات مع الأسعار
- `suppliers` — الموردون
- `customers` — العملاء
- `purchase_invoices` + `purchase_items` — فواتير الشراء
- `sale_invoices` + `sale_items` — فواتير المبيعات
- `stock_movements` — سجل حركات المخزون

---

## ⚙️ متغيرات البيئة

| المتغير | الوصف | الافتراضي |
|---------|-------|-----------|
| `DATABASE_URL` | رابط قاعدة البيانات | `postgresql://jenan:jenanpass@db:5432/jenan_biz` |
| `SECRET_KEY` | مفتاح JWT | `your-secret-key-change-in-production` |
| `ALGORITHM` | خوارزمية JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | مدة انتهاء التوكن | `1440` (يوم) |
| `TAX_RATE` | نسبة الضريبة | `0.15` (15%) |

---

## 🔒 الأمان

- JWT Authentication لجميع نقاط النهاية المحمية
- تشفير كلمات المرور باستخدام bcrypt
- CORS مُهيأ للتطوير (يجب تقييده في الإنتاج)
- التحقق من صحة المدخلات عبر Pydantic

---

## 📄 الترخيص

MIT License
