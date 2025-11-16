# دليل البدء السريع
# Quick Start Guide

---

## 🚀 البدء في 5 دقائق

### الخطوة 1: تحميل الملفات

```bash
# انسخ ملف iiot_platform_complete.zip إلى جهازك
unzip iiot_platform_complete.zip
cd iiot_platform
```

### الخطوة 2: تثبيت المتطلبات

**على Windows:**

```bash
# تثبيت Python 3.8
# من https://www.python.org/downloads/release/python-3810/

# تثبيت Node.js 12
# من https://nodejs.org/dist/v12.22.12/node-v12.22.12-x86.msi

# تثبيت المكتبات
cd backend
pip install fastapi uvicorn pydantic pandas numpy scikit-learn python-jose passlib python-dotenv
```

**على Linux/Mac:**

```bash
# تثبيت Python و Node.js
sudo apt install python3 python3-pip nodejs npm

# تثبيت المكتبات
cd backend
pip install -r requirements.txt
```

### الخطوة 3: تشغيل الخادم

```bash
# Terminal 1: تشغيل Backend
cd backend
python main.py

# Terminal 2: تشغيل Frontend
cd frontend
npm install
npm run dev
```

### الخطوة 4: الدخول

افتح المتصفح:

```
http://localhost:3000
```

---

## 📁 هيكل المشروع

```
iiot_platform/
├── backend/                 # الخلفية (Python/FastAPI)
│   ├── main.py             # الملف الرئيسي
│   ├── models.py           # نماذج البيانات
│   ├── requirements.txt     # المكتبات
│   ├── database/           # اتصالات قواعد البيانات
│   ├── services/           # الخدمات
│   ├── routes/             # مسارات API
│   └── kafka_broker/       # Kafka
├── frontend/               # الواجهة الأمامية (React)
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml      # تكوين Docker
├── .env                    # متغيرات البيئة
├── README.md              # التوثيق الرئيسي
├── DOCUMENTATION.md       # التوثيق الشامل
├── PROJECT_SUMMARY.md     # ملخص المشروع
├── DEPLOYMENT_GUIDE.md    # دليل النشر
└── BACKUP_RESTORE_GUIDE.md # دليل النسخ الاحتياطية
```

---

## 🔧 الأوامر الأساسية

### تشغيل Backend

```bash
cd backend
python main.py
```

### تشغيل Frontend

```bash
cd frontend
npm run dev
```

### تثبيت المكتبات

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### بناء Frontend للإنتاج

```bash
cd frontend
npm run build
```

---

## 🌐 الروابط الرئيسية

| الخدمة | الرابط |
|--------|--------|
| **الواجهة الأمامية** | http://localhost:3000 |
| **توثيق API** | http://localhost:8000/docs |
| **Swagger UI** | http://localhost:8000/redoc |

---

## ⚙️ متغيرات البيئة

إنشئ ملف `.env` في جذر المشروع:

```env
# Backend
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/iiot_db
MONGODB_URL=mongodb://localhost:27017/iiot_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

---

## 🐛 استكشاف الأخطاء

### خطأ: "Port already in use"

```bash
# على Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# على Mac/Linux
lsof -i :8000
kill -9 <PID>
```

### خطأ: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### خطأ: "npm: command not found"

تأكد من تثبيت Node.js:

```bash
node --version
npm --version
```

---

## 📊 الإحصائيات

| المقياس | القيمة |
|--------|--------|
| **عدد مسارات API** | 25+ |
| **عدد صفحات الواجهة الأمامية** | 6 |
| **عدد نماذج ML** | 4 |
| **سطور الكود** | 3500+ |

---

## 🎯 الخطوات التالية

1. **اقرأ التوثيق الكامل:** `DOCUMENTATION.md`
2. **اقرأ دليل النشر:** `DEPLOYMENT_GUIDE.md`
3. **اقرأ دليل النسخ الاحتياطية:** `BACKUP_RESTORE_GUIDE.md`
4. **استكشف الكود:** `backend/main.py` و `frontend/src/App.jsx`

---

## 💡 نصائح مفيدة

### 1. استخدام Virtual Environment

```bash
# Python
python -m venv venv
source venv/bin/activate  # على Mac/Linux
venv\Scripts\activate     # على Windows
```

### 2. تثبيت المكتبات بسرعة

```bash
pip install -r requirements.txt --upgrade
```

### 3. تشغيل في وضع التطوير

```bash
# Backend
python main.py --debug

# Frontend
npm run dev
```

### 4. بناء صورة Docker

```bash
docker build -t iiot-platform .
docker run -p 8000:8000 iiot-platform
```

---

## 📞 الدعم والمساعدة

- **البريد الإلكتروني:** support@iiot-platform.com
- **التوثيق:** اقرأ `DOCUMENTATION.md`
- **المشاكل:** اقرأ `QUICK_START.md` (هذا الملف)

---

**استمتع بـ منصة IoT المتقدمة! 🚀**
