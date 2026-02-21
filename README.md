# نظام جنان بيز - نظام المحاسبة والإدارة التجارية

<div dir="rtl">

## 📋 نظرة عامة

نظام محاسبي متكامل يشمل إدارة المنتجات، الموردين، العملاء، فواتير المشتريات والمبيعات، وإدارة المخزون. مبني بـ **FastAPI** (Python) للخلفية و **React** للواجهة الأمامية.

---

## 🚀 الميزات الرئيسية

- **نظام تسجيل دخول آمن** (JWT)
- **إدارة المنتجات** - إضافة، تعديل، حذف مع تتبع المخزون
- **إدارة الموردين والعملاء** - كاملة
- **فواتير المشتريات** - مع تحديث المخزون تلقائياً ورفع PDF
- **فواتير المبيعات** - مع حساب الربح تلقائياً
- **إدارة المخزون** - عرض الكميات، تنبيهات المخزون المنخفض، سجل الحركات
- **حساب الضريبة 15%** - اختياري لكل فاتورة
- **واجهة احترافية** - Tailwind CSS، دعم RTL العربي
- **لوحة تحكم** - إحصائيات شاملة

---

## 🛠️ متطلبات التشغيل

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (اختياري)

---

## ⚡ التشغيل السريع باستخدام Docker

```bash
# 1. استنساخ المشروع
git clone https://github.com/jenan1977/jenan-biz.git
cd jenan-biz

# 2. تشغيل قاعدة البيانات
cd backend
docker-compose up -d db

# 3. إعداد متغيرات البيئة
cp .env.example .env
# عدّل .env حسب بيئتك

# 4. تثبيت المكتبات وتشغيل الـ migrations
pip install -r requirements.txt
alembic upgrade head

# 5. إضافة بيانات تجريبية (اختياري)
python seed.py

# 6. تشغيل الخادم
uvicorn app.main:app --reload --port 8000
```

---

## 🖥️ تشغيل الواجهة الأمامية

```bash
cd frontend

# تثبيت الاعتماديات
npm install

# تشغيل بيئة التطوير
npm run dev

# البناء للإنتاج
npm run build
```

الواجهة ستكون متاحة على: **http://localhost:5173**

---

## 📁 هيكل المشروع

```
jenan-biz/
├── backend/
│   ├── app/
│   │   ├── auth/          # المصادقة وإدارة المستخدمين
│   │   ├── models/        # نماذج قاعدة البيانات
│   │   ├── schemas/       # مخططات البيانات (Pydantic)
│   │   ├── routes/        # مسارات الـ API
│   │   ├── services/      # منطق العمل
│   │   ├── utils/         # أدوات مساعدة
│   │   ├── main.py        # نقطة دخول التطبيق
│   │   ├── config.py      # الإعدادات
│   │   └── database.py    # إعداد قاعدة البيانات
│   ├── alembic/           # ملفات الـ migrations
│   ├── requirements.txt
│   ├── seed.py
│   ├── Dockerfile
│   └── docker-compose.yml
└── frontend/
    ├── src/
    │   ├── components/    # المكونات المشتركة
    │   ├── pages/         # صفحات التطبيق
    │   ├── services/      # خدمات الـ API
    │   └── context/       # React Context
    ├── package.json
    └── index.html
```

---

## 🔐 بيانات الدخول الافتراضية (بعد تشغيل seed.py)

| الحقل | القيمة |
|-------|--------|
| البريد الإلكتروني | admin@jenan.com |
| كلمة المرور | admin123 |

---

## 📡 توثيق الـ API

بعد تشغيل الخادم، يمكن الوصول إلى توثيق الـ API التفاعلي على:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🗃️ نماذج قاعدة البيانات

| الجدول | الوصف |
|--------|-------|
| `users` | المستخدمون والمشرفون |
| `products` | المنتجات |
| `suppliers` | الموردون |
| `customers` | العملاء |
| `purchase_invoices` | فواتير المشتريات |
| `purchase_items` | بنود فاتورة الشراء |
| `invoices` | فواتير المبيعات |
| `invoice_items` | بنود فاتورة البيع |
| `stock` | المخزون الحالي |
| `stock_movements` | سجل حركات المخزون |
| `payments` | المدفوعات |

---

## ⚙️ متغيرات البيئة

```env
DATABASE_URL=postgresql://user:password@localhost:5432/jenan_biz
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=uploads
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🐳 التشغيل الكامل بـ Docker Compose

```bash
cd backend
docker-compose up --build
```

يشغّل: قاعدة البيانات + خادم الـ API معاً.

---

## 📝 الترخيص

هذا المشروع مرخص بموجب MIT License.

</div>
