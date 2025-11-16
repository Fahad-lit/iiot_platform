# دليل نشر منصة IoT على السيرفرات الخارجية
# Deployment Guide for IoT Platform on External Servers

**الإصدار:** 1.0.0  
**التاريخ:** نوفمبر 2025  
**الحالة:** جاهز للنشر

---

## 📋 المحتويات

1. [Heroku](#heroku)
2. [DigitalOcean](#digitalocean)
3. [AWS](#aws)
4. [Render](#render)
5. [Railway](#railway)

---

## 🚀 Heroku

### المتطلبات:
- حساب Heroku (مجاني)
- Heroku CLI

### خطوات التثبيت:

#### 1. تثبيت Heroku CLI

```bash
# Windows
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. تسجيل الدخول

```bash
heroku login
```

#### 3. إنشاء تطبيق جديد

```bash
heroku create your-app-name
```

#### 4. إضافة ملف Procfile

أنشئ ملف باسم `Procfile` في جذر المشروع:

```
web: cd backend && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

#### 5. إضافة ملف requirements.txt

```bash
cd backend
pip freeze > requirements.txt
```

#### 6. إضافة ملف runtime.txt

```
python-3.11.0
```

#### 7. نشر التطبيق

```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

#### 8. الوصول إلى التطبيق

```
https://your-app-name.herokuapp.com
```

---

## 🌐 DigitalOcean

### المتطلبات:
- حساب DigitalOcean (مدفوع من $5/شهر)
- Droplet (VPS)

### خطوات التثبيت:

#### 1. إنشاء Droplet

1. اذهب إلى DigitalOcean.com
2. اضغط "Create" → "Droplets"
3. اختر:
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** $5/month (كافي للبداية)
   - **Region:** الأقرب إليك

#### 2. الاتصال بـ Droplet

```bash
ssh root@your_droplet_ip
```

#### 3. تثبيت المتطلبات

```bash
# تحديث النظام
apt update && apt upgrade -y

# تثبيت Python و Node.js
apt install python3 python3-pip nodejs npm -y

# تثبيت Docker (اختياري)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

#### 4. تحميل ملفات المشروع

```bash
# استخدام Git
git clone https://github.com/your-repo/iiot_platform.git
cd iiot_platform

# أو استخدام SCP
scp -r iiot_platform root@your_droplet_ip:/root/
```

#### 5. تثبيت المكتبات

```bash
cd backend
pip install -r requirements.txt
```

#### 6. تشغيل التطبيق

```bash
# استخدام systemd للتشغيل التلقائي
sudo nano /etc/systemd/system/iiot.service
```

أضف:

```ini
[Unit]
Description=IIoT Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/iiot_platform/backend
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

ثم:

```bash
sudo systemctl enable iiot
sudo systemctl start iiot
```

#### 7. إعداد Nginx (اختياري)

```bash
apt install nginx -y
sudo nano /etc/nginx/sites-available/default
```

أضف:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

ثم:

```bash
sudo systemctl restart nginx
```

---

## ☁️ AWS

### المتطلبات:
- حساب AWS
- EC2 Instance

### خطوات التثبيت:

#### 1. إنشاء EC2 Instance

1. اذهب إلى AWS Console
2. اختر EC2
3. اضغط "Launch Instance"
4. اختر:
   - **AMI:** Ubuntu 22.04 LTS
   - **Instance Type:** t2.micro (مجاني في السنة الأولى)

#### 2. إعداد Security Group

أضف:
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 8000 (Backend)
- Port 3000 (Frontend)

#### 3. الاتصال بـ Instance

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 4. تثبيت المتطلبات

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip nodejs npm -y
```

#### 5. تحميل ملفات المشروع

```bash
git clone https://github.com/your-repo/iiot_platform.git
cd iiot_platform
```

#### 6. تثبيت المكتبات

```bash
cd backend
pip install -r requirements.txt
```

#### 7. تشغيل التطبيق

```bash
python3 main.py
```

---

## 🎨 Render

### المتطلبات:
- حساب Render (مجاني + مدفوع)

### خطوات التثبيت:

#### 1. إنشاء Web Service

1. اذهب إلى Render.com
2. اضغط "New +" → "Web Service"
3. اختر GitHub repository

#### 2. إعدادات التطبيق

- **Build Command:** `cd backend && pip install -r requirements.txt`
- **Start Command:** `cd backend && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker`

#### 3. النشر التلقائي

Render سيقوم بالنشر التلقائي عند كل push إلى GitHub.

---

## 🚂 Railway

### المتطلبات:
- حساب Railway

### خطوات التثبيت:

#### 1. ربط GitHub

1. اذهب إلى Railway.app
2. اضغط "New Project"
3. اختر "Deploy from GitHub"

#### 2. اختر Repository

اختر `iiot_platform`

#### 3. إضافة متغيرات البيئة

```
PYTHON_VERSION=3.11
NODE_VERSION=18
```

#### 4. النشر التلقائي

Railway سيقوم بالنشر التلقائي.

---

## 📊 مقارنة السيرفرات

| السيرفر | السعر | السهولة | الأداء | الدعم |
|--------|------|--------|--------|-------|
| **Heroku** | مجاني/مدفوع | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ممتاز |
| **DigitalOcean** | $5+/شهر | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | جيد |
| **AWS** | مجاني (سنة)/مدفوع | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ممتاز |
| **Render** | مجاني/مدفوع | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | جيد |
| **Railway** | مدفوع | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | جيد |

---

## 🔒 نصائح الأمان

### 1. استخدام متغيرات البيئة

```bash
# لا تضع كلمات المرور مباشرة في الكود
# استخدم متغيرات البيئة
export DATABASE_URL="postgresql://..."
export SECRET_KEY="your-secret-key"
```

### 2. استخدام HTTPS

جميع السيرفرات توفر شهادات SSL مجانية.

### 3. تحديث المكتبات

```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### 4. النسخ الاحتياطية

قم بعمل نسخ احتياطية منتظمة من قاعدة البيانات.

---

## 🆘 استكشاف الأخطاء

### خطأ: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### خطأ: "Connection refused"

تأكد من أن جميع الخدمات تعمل:

```bash
# على Heroku
heroku logs --tail

# على DigitalOcean
journalctl -u iiot -f
```

### خطأ: "Port already in use"

```bash
# تغيير المنفذ
python main.py --port 8001
```

---

## 📞 الدعم والمساعدة

- **Heroku:** https://devcenter.heroku.com/
- **DigitalOcean:** https://www.digitalocean.com/docs/
- **AWS:** https://docs.aws.amazon.com/
- **Render:** https://render.com/docs
- **Railway:** https://docs.railway.app/

---

**تم الإنجاز! المنصة جاهزة للنشر على أي سيرفر خارجي! 🎉**
