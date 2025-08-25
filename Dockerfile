# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين مجلد العمل
WORKDIR /app

# تثبيت الأدوات الأساسية بما في ذلك docker-compose
RUN apt-get update && apt-get install -y \
    curl \
    && curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose \
    && apt-get clean

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# تعيين متغير البيئة للبايثون
ENV PYTHONUNBUFFERED=1

# استخدام السكربت كأمر بداية
CMD ["bash entrypoint.sh"]