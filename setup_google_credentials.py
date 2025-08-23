#!/usr/bin/env python3
"""
سكريبت لإعداد بيانات اعتماد Google Drive API
"""

import json
import os

def create_credentials_template():
    """إنشاء قالب لملف بيانات الاعتماد"""
    
    credentials_template = {
        "installed": {
            "client_id": "your_client_id.apps.googleusercontent.com",
            "project_id": "your_project_id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your_client_secret",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }
    
    with open('credentials_template.json', 'w', encoding='utf-8') as f:
        json.dump(credentials_template, f, indent=2, ensure_ascii=False)
    
    print("✅ تم إنشاء ملف credentials_template.json")
    print("\n📋 خطوات الإعداد:")
    print("1. اذهب إلى Google Cloud Console: https://console.cloud.google.com/")
    print("2. أنشئ مشروع جديد أو اختر مشروع موجود")
    print("3. فعّل Google Drive API")
    print("4. أنشئ بيانات اعتماد OAuth 2.0")
    print("5. نزّل ملف JSON وأعد تسميته إلى credentials.json")
    print("6. ضع الملف في نفس مجلد البوت")

def validate_credentials():
    """التحقق من صحة ملف بيانات الاعتماد"""
    
    if not os.path.exists('credentials.json'):
        print("❌ ملف credentials.json غير موجود")
        return False
    
    try:
        with open('credentials.json', 'r', encoding='utf-8') as f:
            creds = json.load(f)
        
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        
        if 'installed' in creds:
            creds_data = creds['installed']
        elif 'web' in creds:
            creds_data = creds['web']
        else:
            print("❌ تنسيق ملف بيانات الاعتماد غير صحيح")
            return False
        
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ حقول مفقودة في ملف بيانات الاعتماد: {missing_fields}")
            return False
        
        print("✅ ملف بيانات الاعتماد صحيح")
        return True
        
    except json.JSONDecodeError:
        print("❌ خطأ في تنسيق ملف JSON")
        return False
    except Exception as e:
        print(f"❌ خطأ في قراءة ملف بيانات الاعتماد: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إعداد بيانات اعتماد Google Drive API")
    print("=" * 50)
    
    if os.path.exists('credentials.json'):
        print("📁 تم العثور على ملف credentials.json")
        if validate_credentials():
            print("✅ الإعداد مكتمل!")
        else:
            print("❌ يرجى مراجعة ملف بيانات الاعتماد")
    else:
        print("📁 لم يتم العثور على ملف credentials.json")
        create_credentials_template()

if __name__ == '__main__':
    main()

