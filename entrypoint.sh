#!/bin/sh
# إنشاء credentials.json من متغير البيئة
python3 -c 'import os,json; open("credentials.json","w").write(os.getenv("GOOGLE_CREDENTIALS","{}") or "{}")'
# تشغيل docker-compose
docker-compose up
