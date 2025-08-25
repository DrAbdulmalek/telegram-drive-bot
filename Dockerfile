# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# تعيين متغير البيئة للبايثون
ENV PYTHONUNBUFFERED=1

# إنشاء credentials.json من متغير البيئة
RUN python3 -c 'import os,json; open("credentials.json","w").write(os.getenv("GOOGLE_CREDENTIALS","{}") or "{}")'

# الأمر الافتراضي لتشغيل البوت
CMD ["python3", "telegram_drive_bot.py"]