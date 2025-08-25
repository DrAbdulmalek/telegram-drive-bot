# دليل الإعداد المفصل - بوت تيليجرام لرفع الملفات إلى Google Drive

## 📋 جدول المحتويات

1. [المتطلبات الأساسية](#المتطلبات-الأساسية)
2. [إنشاء بوت تيليجرام](#إنشاء-بوت-تيليجرام)
3. [إعداد Google Drive API](#إعداد-google-drive-api)
4. [تثبيت وتشغيل البوت](#تثبيت-وتشغيل-البوت)
5. [النشر على الخدمات المجانية](#النشر-على-الخدمات-المجانية)
6. [استكشاف الأخطاء](#استكشاف-الأخطاء)

## 🔧 المتطلبات الأساسية

### البرامج المطلوبة:
- **Python 3.9+** - [تحميل من هنا](https://www.python.org/downloads/)
- **Git** - [تحميل من هنا](https://git-scm.com/downloads/)
- **محرر نصوص** (VS Code, Notepad++, إلخ)

### الحسابات المطلوبة:
- حساب تيليجرام
- حساب Google (Gmail)
- حساب GitHub (للنشر)

## 🤖 إنشاء بوت تيليجرام

### الخطوة 1: التواصل مع BotFather

1. افتح تيليجرام
2. ابحث عن `@BotFather`
3. ابدأ محادثة معه

### الخطوة 2: إنشاء البوت

أرسل الأوامر التالية:

```
/newbot
```

### الخطوة 3: تسمية البوت

```
اسم البوت: My Drive Bot
اسم المستخدم: mydrive_upload_bot
```

**ملاحظة:** اسم المستخدم يجب أن ينتهي بـ `bot`

### الخطوة 4: حفظ الرمز

ستحصل على رسالة تحتوي على:
```
Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**احفظ هذا الرمز بعناية!**

## 🔐 إعداد Google Drive API

### الخطوة 1: إنشاء مشروع Google Cloud

1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. سجل دخولك بحساب Google
3. اضغط على "Select a project" في الأعلى
4. اضغط "NEW PROJECT"
5. أدخل اسم المشروع: `Telegram Drive Bot`
6. اضغط "CREATE"

### الخطوة 2: تفعيل Google Drive API

1. في القائمة الجانبية، اذهب إلى "APIs & Services" > "Library"
2. ابحث عن "Google Drive API"
3. اضغط على النتيجة الأولى
4. اضغط "ENABLE"

### الخطوة 3: إنشاء بيانات الاعتماد

1. اذهب إلى "APIs & Services" > "Credentials"
2. اضغط "CREATE CREDENTIALS" > "OAuth 2.0 Client IDs"

### الخطوة 4: إعداد OAuth consent screen

إذا لم تكن قد أعددته من قبل:

1. اضغط "CONFIGURE CONSENT SCREEN"
2. اختر "External"
3. املأ المعلومات المطلوبة:
   - App name: `Telegram Drive Bot`
   - User support email: بريدك الإلكتروني
   - Developer contact: بريدك الإلكتروني
4. اضغط "SAVE AND CONTINUE"
5. في صفحة "Scopes"، اضغط "SAVE AND CONTINUE"
6. في صفحة "Test users"، أضف بريدك الإلكتروني
7. اضغط "SAVE AND CONTINUE"

### الخطوة 5: إنشاء OAuth 2.0 Client

1. ارجع إلى "Credentials"
2. اضغط "CREATE CREDENTIALS" > "OAuth 2.0 Client IDs"
3. اختر "Desktop application"
4. أدخل الاسم: `Telegram Bot Client`
5. اضغط "CREATE"

### الخطوة 6: تحميل ملف JSON

1. ستظهر نافذة مع تفاصيل العميل
2. اضغط "DOWNLOAD JSON"
3. احفظ الملف باسم `credentials.json`

## 💻 تثبيت وتشغيل البوت

### الخطوة 1: تحميل المشروع

```bash
git clone https://github.com/yourusername/telegram-drive-bot.git
cd telegram-drive-bot
```

### الخطوة 2: تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### الخطوة 3: إعداد ملف البيئة

1. انسخ ملف المثال:
```bash
cp .env.example .env
```

2. حرر ملف `.env`:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### الخطوة 4: وضع ملف بيانات الاعتماد

ضع ملف `credentials.json` في نفس مجلد المشروع.

### الخطوة 5: اختبار الإعداد

```bash
python3 setup_google_credentials.py
```

### تشغيل البوت
- للملفات الصغيرة (حتى 20 ميجابايت):
  ```bash
  python3 telegram_drive_bot.py

للملفات الكبيرة (حتى 2 جيجابايت):
bashpython3 telegram_drive_bot_large_files.py
ملاحظة: يتطلب تشغيل الملفات الكبيرة إعداد خادم Telegram Bot API المحلي باستخدام Docker (راجع LARGE_FILES_GUIDE.md).


إذا ظهرت رسالة "بدء تشغيل البوت..." فكل شيء يعمل بشكل صحيح!

## 🌐 النشر على الخدمات المجانية

### خيار 1: Render.com (الأسهل)

#### الخطوة 1: رفع المشروع إلى GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/telegram-drive-bot.git
git push -u origin main
```

#### الخطوة 2: إنشاء حساب على Render

1. اذهب إلى [render.com](https://render.com)
2. سجل باستخدام GitHub
3. اضغط "New" > "Web Service"
4. اختر مستودع GitHub الخاص بك

#### الخطوة 3: إعداد الخدمة

- **Name:** `telegram-drive-bot`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python3 telegram_drive_bot.py`

#### الخطوة 4: إضافة متغيرات البيئة

في قسم "Environment Variables":
- `TELEGRAM_BOT_TOKEN`: رمز البوت
- `GOOGLE_CREDENTIALS_FILE`: `credentials.json`

#### الخطوة 5: رفع ملف بيانات الاعتماد

يمكنك إما:
1. إضافة محتوى `credentials.json` كمتغير بيئة
2. أو استخدام خدمة أخرى لحفظ الملف

#### الخطوة 6: النشر

اضغط "Create Web Service" وانتظر اكتمال النشر.

### خيار 2: Railway.app

```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# إنشاء مشروع
railway new

# إضافة متغيرات البيئة
railway variables set TELEGRAM_BOT_TOKEN=your_token_here

# نشر المشروع
railway up
```

### خيار 3: Fly.io

```bash
# تثبيت Fly CLI
curl -L https://fly.io/install.sh | sh

# تسجيل الدخول
flyctl auth login

# إنشاء تطبيق
flyctl launch

# إضافة متغيرات البيئة
flyctl secrets set TELEGRAM_BOT_TOKEN=your_token_here

# نشر
flyctl deploy
```

## 🔍 استكشاف الأخطاء

### مشكلة: "No module named 'telegram'"

**الحل:**
```bash
pip install python-telegram-bot
```

### مشكلة: "credentials.json not found"

**الحل:**
1. تأكد من وجود الملف في مجلد المشروع
2. تحقق من اسم الملف (يجب أن يكون `credentials.json` بالضبط)
3. تأكد من صحة مسار الملف في `.env`

### مشكلة: "Invalid token"

**الحل:**
1. تحقق من رمز البوت في ملف `.env`
2. تأكد من عدم وجود مسافات إضافية
3. جرب إنشاء بوت جديد من @BotFather

### مشكلة: "Google API quota exceeded"

**الحل:**
1. انتظر بعض الوقت (عادة 24 ساعة)
2. تحقق من حدود الاستخدام في Google Cloud Console
3. فكر في ترقية الحساب إذا لزم الأمر

### مشكلة: البوت يعمل محلياً لكن لا يعمل بعد النشر

**الحل:**
1. تحقق من سجلات الخطأ في منصة الاستضافة
2. تأكد من إضافة جميع متغيرات البيئة
3. تحقق من أن ملف `credentials.json` متاح

### مشكلة: "File too large"

**الحل:**
- حجم الملف يتجاوز 20 ميجابايت (حد تيليجرام)
- اضغط الملف أو قسمه إلى أجزاء أصغر

## 📞 الحصول على المساعدة

إذا واجهت مشاكل أخرى:

1. راجع [Issues على GitHub](https://github.com/yourusername/telegram-drive-bot/issues)
2. أنشئ Issue جديد مع تفاصيل المشكلة
3. تأكد من تضمين:
   - نظام التشغيل
   - إصدار Python
   - رسالة الخطأ الكاملة
   - الخطوات التي أدت للمشكلة

## ✅ قائمة التحقق النهائية

قبل النشر، تأكد من:

- [ ] البوت يعمل محلياً
- [ ] ملف `credentials.json` موجود وصحيح
- [ ] متغيرات البيئة مضبوطة
- [ ] تم اختبار رفع ملف تجريبي
- [ ] Google Drive API مفعل
- [ ] البوت يستجيب للأوامر

---

**تهانينا! 🎉 بوتك جاهز الآن للعمل!**

