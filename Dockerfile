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

# تشغيل البوت
CMD ["python3", "telegram_drive_bot.py"]

