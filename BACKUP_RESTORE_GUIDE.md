# دليل النسخ الاحتياطية والاستعادة
# Backup and Restore Guide

---

## 📦 النسخ الاحتياطية (Backup)

### الطريقة 1: النسخ الاحتياطية اليدوية

#### 1. إنشاء ملف ZIP

```bash
cd /home/ubuntu
zip -r iiot_platform_backup_$(date +%Y%m%d_%H%M%S).zip iiot_platform/
```

هذا سينشئ ملف مثل: `iiot_platform_backup_20251107_120000.zip`

#### 2. حفظ النسخة الاحتياطية

**على Google Drive:**

```bash
# استخدم Google Drive API أو اسحب الملف يدويًا
```

**على Dropbox:**

```bash
# استخدم Dropbox API أو اسحب الملف يدويًا
```

**على OneDrive:**

```bash
# استخدم OneDrive API أو اسحب الملف يدويًا
```

---

### الطريقة 2: النسخ الاحتياطية التلقائية (GitHub)

#### 1. إنشاء مستودع GitHub خاص

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/iiot_platform.git
git push -u origin main
```

#### 2. إعداد النسخ الاحتياطية التلقائية

GitHub يحفظ جميع التغييرات تلقائياً!

#### 3. الوصول إلى النسخ الاحتياطية

```bash
# عرض السجل
git log

# الرجوع إلى نسخة قديمة
git checkout <commit-hash>

# استعادة الملف
git restore <filename>
```

---

### الطريقة 3: النسخ الاحتياطية على السيرفر

#### على DigitalOcean:

```bash
# إنشاء نسخة احتياطية يومية
sudo crontab -e

# أضف هذا السطر:
0 2 * * * cd /root/iiot_platform && zip -r /backups/iiot_backup_$(date +\%Y\%m\%d).zip . > /dev/null 2>&1
```

#### على AWS:

استخدم AWS Backup أو S3:

```bash
# تثبيت AWS CLI
pip install awscli

# إنشاء نسخة احتياطية
aws s3 sync /root/iiot_platform s3://my-backup-bucket/iiot_platform/
```

---

## 🔄 الاستعادة (Restore)

### الطريقة 1: استعادة من ملف ZIP

#### 1. تحميل الملف

```bash
# انسخ الملف إلى السيرفر
scp iiot_platform_backup_20251107_120000.zip root@your_server:/root/
```

#### 2. فك الضغط

```bash
cd /root
unzip iiot_platform_backup_20251107_120000.zip
```

#### 3. إعادة التثبيت

```bash
cd iiot_platform/backend
pip install -r requirements.txt
python main.py
```

---

### الطريقة 2: استعادة من GitHub

#### 1. استنساخ المستودع

```bash
git clone https://github.com/your-username/iiot_platform.git
cd iiot_platform
```

#### 2. الرجوع إلى نسخة قديمة (اختياري)

```bash
# عرض السجل
git log

# الرجوع إلى نسخة معينة
git checkout <commit-hash>
```

#### 3. إعادة التثبيت

```bash
cd backend
pip install -r requirements.txt
python main.py
```

---

### الطريقة 3: استعادة من AWS S3

```bash
# تثبيت AWS CLI
pip install awscli

# استعادة الملفات
aws s3 sync s3://my-backup-bucket/iiot_platform/ /root/iiot_platform/

# إعادة التثبيت
cd /root/iiot_platform/backend
pip install -r requirements.txt
python main.py
```

---

## 📋 جدول النسخ الاحتياطية الموصى به

| التكرار | الطريقة | التخزين |
|--------|--------|--------|
| **يومي** | GitHub | مجاني |
| **أسبوعي** | Google Drive | مجاني |
| **شهري** | AWS S3 | مدفوع |

---

## ✅ قائمة التحقق من النسخ الاحتياطية

قبل كل نسخة احتياطية، تأكد من:

- [ ] جميع الملفات محدثة
- [ ] قاعدة البيانات محفوظة
- [ ] ملفات الإعدادات آمنة
- [ ] لا توجد ملفات مؤقتة
- [ ] جميع المكتبات محدثة

---

## 🔐 نصائح الأمان

### 1. لا تحفظ كلمات المرور

```bash
# ❌ خطأ
DATABASE_PASSWORD=12345

# ✅ صحيح
# استخدم متغيرات البيئة
export DATABASE_PASSWORD=12345
```

### 2. استخدم .gitignore

```bash
# في ملف .gitignore
.env
*.log
node_modules/
__pycache__/
.DS_Store
```

### 3. تشفير النسخ الاحتياطية

```bash
# تشفير الملف
gpg -c iiot_platform_backup.zip

# فك التشفير
gpg iiot_platform_backup.zip.gpg
```

---

## 📊 مثال عملي: النسخ الاحتياطية اليومية

### السيناريو:

أنت تريد نسخة احتياطية يومية على Google Drive.

### الحل:

#### 1. إنشاء سكريبت

```bash
# backup.sh
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
PROJECT_DIR="/home/ubuntu/iiot_platform"
DATE=$(date +%Y%m%d_%H%M%S)

# إنشاء مجلد النسخ الاحتياطية
mkdir -p $BACKUP_DIR

# إنشاء النسخة الاحتياطية
zip -r $BACKUP_DIR/iiot_backup_$DATE.zip $PROJECT_DIR/ -q

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.zip" -mtime +30 -delete

echo "✅ تم إنشاء نسخة احتياطية: iiot_backup_$DATE.zip"
```

#### 2. إضافة إلى cron

```bash
crontab -e

# أضف هذا السطر (كل يوم الساعة 2 صباحاً)
0 2 * * * /home/ubuntu/backup.sh
```

#### 3. رفع إلى Google Drive

```bash
# استخدم Rclone
curl https://rclone.org/install.sh | sudo bash
rclone config create gdrive drive
rclone sync /home/ubuntu/backups gdrive:backups
```

---

## 🆘 حالات الطوارئ

### حالة 1: حذف ملف بالخطأ

```bash
# استعادة من GitHub
git restore <filename>

# أو من النسخة الاحتياطية
unzip iiot_platform_backup.zip
cp iiot_platform/<filename> .
```

### حالة 2: تلف قاعدة البيانات

```bash
# استعادة من النسخة الاحتياطية
rm -rf /root/iiot_platform
unzip iiot_platform_backup.zip -d /root/
```

### حالة 3: اختراق النظام

```bash
# استعادة من نسخة احتياطية قديمة معروفة أنها آمنة
git checkout <safe-commit-hash>
```

---

## 📞 الدعم

إذا واجهت مشكلة في النسخ الاحتياطية:

1. تأكد من وجود مساحة تخزين كافية
2. تحقق من صلاحيات الملفات
3. جرب النسخ الاحتياطية اليدوية أولاً
4. احتفظ بنسخ متعددة

---

**تذكر: النسخ الاحتياطية المنتظمة تحميك من فقدان البيانات! 🔒**
