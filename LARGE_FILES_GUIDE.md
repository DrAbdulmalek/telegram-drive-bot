# دليل شامل لدعم الملفات الكبيرة - بوت تيليجرام Google Drive

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية تمكين دعم الملفات الكبيرة (حتى 2 جيجابايت) في بوت تيليجرام لرفع الملفات إلى Google Drive.

## 📊 مقارنة الحلول

### الحل العادي (Bot API الافتراضي)
- **الحد الأقصى:** 20 ميجابايت
- **الإعداد:** بسيط جداً
- **الموارد:** لا يتطلب موارد إضافية
- **الاستخدام:** مناسب للملفات الصغيرة والمتوسطة

### الحل المتقدم (Local Bot API Server)
- **الحد الأقصى:** 2 جيجابايت
- **الإعداد:** يتطلب Docker وإعداد إضافي
- **الموارد:** يحتاج 4+ جيجابايت RAM
- **الاستخدام:** مناسب للملفات الكبيرة والمشاريع المتقدمة

## 🔧 الإعداد التفصيلي للملفات الكبيرة

### المرحلة 1: تحضير البيئة

#### تثبيت Docker

**على Windows:**
1. نزّل Docker Desktop من [docker.com](https://www.docker.com/products/docker-desktop)
2. ثبت البرنامج واتبع التعليمات
3. أعد تشغيل الكمبيوتر
4. تحقق من التثبيت: `docker --version`

**على macOS:**
```bash
# باستخدام Homebrew
brew install --cask docker

# أو نزّل من الموقع الرسمي
# https://www.docker.com/products/docker-desktop
```

**على Linux (Ubuntu/Debian):**
```bash
# تحديث النظام
sudo apt update

# تثبيت Docker
sudo apt install -y docker.io docker-compose

# بدء الخدمة
sudo systemctl start docker
sudo systemctl enable docker

# إضافة المستخدم لمجموعة docker
sudo usermod -aG docker $USER

# إعادة تسجيل الدخول أو تشغيل:
newgrp docker

# التحقق من التثبيت
docker --version
```

### المرحلة 2: الحصول على بيانات اعتماد Telegram

#### إنشاء تطبيق Telegram

1. **اذهب إلى [my.telegram.org](https://my.telegram.org)**
2. **سجل دخولك برقم هاتفك**
3. **اذهب إلى "API development tools"**
4. **أنشئ تطبيق جديد:**
   - **App title:** `My Bot API Server`
   - **Short name:** `mybotapi`
   - **Platform:** `Server`
   - **Description:** `Local Bot API Server for large files`

5. **احفظ المعلومات:**
   - `api_id` (رقم)
   - `api_hash` (نص طويل)

### المرحلة 3: تشغيل خادم Bot API المحلي

#### إنشاء مجلد البيانات

```bash
# إنشاء مجلد لحفظ بيانات الخادم
mkdir -p ~/telegram-bot-api-data
cd ~/telegram-bot-api-data
```

#### تشغيل الخادم باستخدام Docker

```bash
# تشغيل خادم Bot API المحلي
docker run -d \
  --name telegram-bot-api \
  --restart unless-stopped \
  -p 8081:8081 \
  -v $(pwd)/data:/var/lib/telegram-bot-api \
  -e TELEGRAM_API_ID=YOUR_API_ID \
  -e TELEGRAM_API_HASH=YOUR_API_HASH \
  aiogram/telegram-bot-api:latest \
  --api-id=YOUR_API_ID \
  --api-hash=YOUR_API_HASH \
  --local \
  --verbosity=1
```

**⚠️ مهم:** استبدل `YOUR_API_ID` و `YOUR_API_HASH` بالقيم الحقيقية!

#### التحقق من تشغيل الخادم

```bash
# التحقق من حالة الحاوية
docker ps

# عرض سجلات الخادم
docker logs telegram-bot-api

# اختبار الخادم (استبدل TOKEN برمز البوت الحقيقي)
curl "http://localhost:8081/bot<YOUR_BOT_TOKEN>/getMe"
```

### المرحلة 4: إعداد البوت للملفات الكبيرة

#### تحديث ملف البيئة

```bash
# إنشاء أو تحديث ملف .env
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
GOOGLE_CREDENTIALS_FILE=credentials.json
BOT_API_SERVER=http://localhost:8081
EOF
```

#### تشغيل البوت المحدث

```bash
# تشغيل النسخة المحدثة للملفات الكبيرة
python3 telegram_drive_bot_large_files.py
```

## 🧪 اختبار النظام

### اختبار أساسي

```bash
# تشغيل اختبارات النظام
python3 test_large_files_bot.py
```

### اختبار يدوي

1. **أرسل `/start` للبوت**
2. **أرسل `/info` لعرض معلومات الخادم**
3. **تحقق من ظهور "الحد الأقصى: 2048 ميجابايت"**
4. **جرب رفع ملف صغير أولاً**
5. **ثم جرب ملف أكبر من 20 ميجابايت**

## 📈 مراقبة الأداء

### مراقبة استخدام الموارد

```bash
# مراقبة استخدام Docker
docker stats telegram-bot-api

# مراقبة مساحة التخزين
du -sh ~/telegram-bot-api-data/

# مراقبة الذاكرة والمعالج
htop
```

### سجلات مفيدة

```bash
# سجلات خادم Bot API
docker logs -f telegram-bot-api

# سجلات البوت (إذا كان يعمل في الخلفية)
tail -f bot.log

# مراقبة الشبكة
netstat -tlnp | grep 8081
```

## 🔧 استكشاف الأخطاء الشائعة

### مشكلة: "Connection refused to localhost:8081"

**الأسباب المحتملة:**
- خادم Bot API غير يعمل
- Docker غير مثبت أو لا يعمل
- المنفذ 8081 مستخدم من برنامج آخر

**الحلول:**
```bash
# التحقق من حالة Docker
docker ps
docker logs telegram-bot-api

# إعادة تشغيل الخادم
docker restart telegram-bot-api

# التحقق من المنفذ
netstat -tlnp | grep 8081
lsof -i :8081
```

### مشكلة: "Invalid API ID or Hash"

**الحلول:**
1. تحقق من صحة `api_id` و `api_hash`
2. تأكد من عدم وجود مسافات إضافية
3. جرب إنشاء تطبيق جديد على my.telegram.org
4. تأكد من استخدام النوع الصحيح (Server)

### مشكلة: "Out of memory" أو بطء شديد

**الحلول:**
```bash
# زيادة ذاكرة Docker
docker run --memory=4g telegram-bot-api

# تنظيف الملفات المؤقتة
docker exec telegram-bot-api find /tmp -name "*.tmp" -delete

# إعادة تشغيل Docker
sudo systemctl restart docker
```

### مشكلة: "File too large" رغم استخدام الخادم المحلي

**الحلول:**
1. تحقق من متغير `BOT_API_SERVER` في ملف `.env`
2. تأكد من أن البوت يستخدم الخادم المحلي
3. راجع سجلات البوت للتأكد من الاتصال الصحيح

## ⚡ تحسين الأداء

### إعدادات Docker المحسنة

```bash
# تشغيل مع موارد محسنة
docker run -d \
  --name telegram-bot-api \
  --restart unless-stopped \
  --memory=4g \
  --cpus=2 \
  --shm-size=1g \
  -p 8081:8081 \
  -v $(pwd)/data:/var/lib/telegram-bot-api \
  telegram-bot-api \
  --local \
  --verbosity=1 \
  --max-connections=1000
```

### تحسين النظام

```bash
# زيادة حدود الملفات المفتوحة
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# تحسين إعدادات الشبكة
echo "net.core.rmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 🔒 الأمان والحماية

### تأمين الخادم

```bash
# ربط الخادم بـ localhost فقط
docker run -p 127.0.0.1:8081:8081 telegram-bot-api

# استخدام شبكة Docker مخصصة
docker network create telegram-net
docker run --network telegram-net telegram-bot-api
```

### النسخ الاحتياطي

```bash
# نسخ احتياطي لبيانات الخادم
tar -czf telegram-bot-api-backup-$(date +%Y%m%d).tar.gz ~/telegram-bot-api-data/

# نسخ احتياطي لإعدادات البوت
cp .env .env.backup
cp credentials.json credentials.json.backup
```

## 📊 مقاييس الأداء المتوقعة

### أوقات الرفع التقريبية

| حجم الملف | الوقت المتوقع | ملاحظات |
|-----------|----------------|----------|
| 50 ميجابايت | 1-3 دقائق | حسب سرعة الإنترنت |
| 200 ميجابايت | 5-10 دقائق | قد يحتاج صبر |
| 500 ميجابايت | 15-30 دقيقة | تأكد من الاستقرار |
| 1 جيجابايت | 30-60 دقيقة | للملفات الكبيرة جداً |
| 2 جيجابايت | 60-120 دقيقة | الحد الأقصى |

### استهلاك الموارد

- **RAM:** 2-4 جيجابايت أثناء معالجة الملفات الكبيرة
- **CPU:** متوسط أثناء الرفع
- **التخزين:** مؤقت حسب حجم الملف
- **الشبكة:** حسب سرعة الإنترنت

## 🚀 الخطوات التالية

بعد إعداد دعم الملفات الكبيرة بنجاح:

1. **اختبر النظام** مع ملفات مختلفة الأحجام
2. **راقب الأداء** وسجلات النظام
3. **أعد النسخ الاحتياطية** بانتظام
4. **حدث النظام** عند توفر إصدارات جديدة
5. **شارك تجربتك** مع المجتمع

## 📞 الدعم والمساعدة

إذا واجهت مشاكل:

1. راجع قسم استكشاف الأخطاء أعلاه
2. تحقق من [Issues على GitHub](https://github.com/yourusername/telegram-drive-bot/issues)
3. أنشئ Issue جديد مع:
   - تفاصيل النظام
   - سجلات الأخطاء
   - خطوات إعادة إنتاج المشكلة

---

**تهانينا! 🎉 أصبح بوتك الآن يدعم الملفات الكبيرة حتى 2 جيجابايت!**

