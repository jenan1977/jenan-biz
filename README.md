# جنان بيز - نظام محاسبي ذكي متكامل
## Jenan Biz - Smart Integrated Accounting System

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org)

نظام محاسبي احترافي وكامل مبني بتقنيات حديثة يدعم إدارة المبيعات والمشتريات والمخزون والتقارير المالية.

---

## 🏗️ البنية المعمارية

```
jenan-biz/
├── app/                    # Backend (Python + FastAPI)
│   ├── core/               # إعدادات، قاعدة البيانات، الأمان
│   ├── shared/             # النماذج المشتركة، الأدوات، الاستثناءات
│   ├── modules/            # وحدات النظام المستقلة
│   │   ├── auth/           # المصادقة وإدارة المستخدمين
│   │   ├── companies/      # إدارة الشركات (Multi-tenant)
│   │   ├── products/       # المنتجات والفئات
│   │   ├── inventory/      # إدارة المخزون وحركاته
│   │   ├── purchases/      # فواتير الشراء
│   │   ├── sales/          # فواتير البيع
│   │   ├── customers/      # إدارة العملاء
│   │   ├── suppliers/      # إدارة الموردين
│   │   ├── reports/        # تقارير المبيعات والمشتريات والضرائب
│   │   ├── analytics/      # التحليلات والخارطة الحرارية
│   │   ├── payments/       # المدفوعات (Stripe, PayPal, Tap)
│   │   ├── taxes/          # حاسبة ضريبة القيمة المضافة
│   │   └── notifications/  # الإشعارات (Email, SMS)
│   └── main.py
├── frontend/               # Frontend (React + Redux)
│   └── src/
│       ├── components/     # مكونات قابلة للإعادة
│       ├── pages/          # صفحات التطبيق
│       ├── services/       # طبقة الـ API
│       ├── hooks/          # React hooks مخصصة
│       ├── store/          # إدارة الحالة (Redux)
│       └── styles/         # الأنماط والتصميم
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🚀 التشغيل السريع

### باستخدام Docker (الطريقة المُوصى بها)

```bash
# 1. استنسخ المستودع
git clone https://github.com/jenan1977/jenan-biz.git
cd jenan-biz

# 2. انسخ ملف البيئة
cp .env.example .env

# 3. شغّل الخدمات
docker-compose up -d

# 4. افتح المتصفح
# Backend API: http://localhost:8000/api/docs
# Frontend: http://localhost:3000
```

### التطوير المحلي

#### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

---

## 📚 توثيق API

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## ✨ المزايا الرئيسية

- ✅ JWT Authentication & Refresh Tokens
- ✅ Multi-tenant (دعم شركات متعددة)
- ✅ Role-based Access Control (RBAC)
- ✅ Audit Trail لكل العمليات
- ✅ ضريبة القيمة المضافة 15% تلقائياً
- ✅ تقارير: مبيعات، مشتريات، أرباح، ضرائب، مخزون
- ✅ خارطة حرارية للمبيعات وتحليل المنتجات
- ✅ دعم بوابات الدفع: Stripe, PayPal, Tap
- ✅ RTL + دعم كامل للعربية
- ✅ Dark/Light Mode
- ✅ Responsive Design

---

## 🧪 الاختبارات

```bash
pytest --cov=app --cov-report=html
```

---

## 📄 الترخيص

MIT License
