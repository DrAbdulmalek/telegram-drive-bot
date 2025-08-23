#!/usr/bin/env python3
"""
سكريبت اختبار البوت مع دعم الملفات الكبيرة
"""

import os
import sys
import tempfile
import asyncio
from unittest.mock import Mock

def test_imports():
    """اختبار استيراد جميع المكتبات المطلوبة"""
    print("🔍 اختبار استيراد المكتبات...")
    
    try:
        import telegram
        print("✅ telegram - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"❌ telegram - فشل الاستيراد: {e}")
        return False
    
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import Flow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        print("✅ Google APIs - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"❌ Google APIs - فشل الاستيراد: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"❌ aiohttp - فشل الاستيراد: {e}")
        return False
    
    try:
        import tempfile
        import shutil
        print("✅ tempfile & shutil - تم الاستيراد بنجاح")
    except ImportError as e:
        print(f"❌ tempfile & shutil - فشل الاستيراد: {e}")
        return False
    
    return True

def test_large_files_bot_class():
    """اختبار فئة البوت للملفات الكبيرة"""
    print("\n🤖 اختبار فئة البوت للملفات الكبيرة...")
    
    try:
        # استيراد فئة البوت
        sys.path.append('/home/ubuntu')
        from telegram_drive_bot_large_files import TelegramDriveBotLargeFiles
        
        # إنشاء مثيل وهمي
        bot = TelegramDriveBotLargeFiles("test_token", "test_credentials.json")
        
        # التحقق من الخصائص
        assert hasattr(bot, 'telegram_token')
        assert hasattr(bot, 'google_credentials_file')
        assert hasattr(bot, 'bot_api_server')
        assert hasattr(bot, 'MAX_FILE_SIZE_STANDARD')
        assert hasattr(bot, 'MAX_FILE_SIZE_LOCAL')
        
        # اختبار دالة الحد الأقصى للملف
        standard_size = bot.get_max_file_size()
        assert standard_size == 20 * 1024 * 1024  # 20 ميجابايت
        
        # اختبار مع خادم محلي
        bot_local = TelegramDriveBotLargeFiles("test_token", "test_credentials.json", "http://localhost:8081")
        local_size = bot_local.get_max_file_size()
        assert local_size == 2 * 1024 * 1024 * 1024  # 2 جيجابايت
        
        print("✅ فئة البوت للملفات الكبيرة - تم إنشاؤها بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ فئة البوت للملفات الكبيرة - فشل الاختبار: {e}")
        return False

def test_file_size_limits():
    """اختبار حدود أحجام الملفات"""
    print("\n📊 اختبار حدود أحجام الملفات...")
    
    try:
        sys.path.append('/home/ubuntu')
        from telegram_drive_bot_large_files import TelegramDriveBotLargeFiles
        
        # اختبار الخادم العادي
        bot_standard = TelegramDriveBotLargeFiles("test", "test", "https://api.telegram.org")
        standard_limit = bot_standard.get_max_file_size()
        expected_standard = 20 * 1024 * 1024  # 20 ميجابايت
        
        if standard_limit == expected_standard:
            print(f"✅ الخادم العادي - الحد الأقصى: {standard_limit / (1024*1024):.0f} ميجابايت")
        else:
            print(f"❌ الخادم العادي - خطأ في الحد الأقصى")
            return False
        
        # اختبار الخادم المحلي
        bot_local = TelegramDriveBotLargeFiles("test", "test", "http://localhost:8081")
        local_limit = bot_local.get_max_file_size()
        expected_local = 2 * 1024 * 1024 * 1024  # 2 جيجابايت
        
        if local_limit == expected_local:
            print(f"✅ الخادم المحلي - الحد الأقصى: {local_limit / (1024*1024*1024):.0f} جيجابايت")
        else:
            print(f"❌ الخادم المحلي - خطأ في الحد الأقصى")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ اختبار حدود الملفات - خطأ: {e}")
        return False

def test_temp_file_handling():
    """اختبار التعامل مع الملفات المؤقتة"""
    print("\n📁 اختبار التعامل مع الملفات المؤقتة...")
    
    try:
        # إنشاء ملف مؤقت للاختبار
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_data = b"This is a test for temp file" * 1000  # بيانات اختبار
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        
        # التحقق من وجود الملف
        if os.path.exists(temp_file_path):
            print(f"✅ تم إنشاء ملف مؤقت: {temp_file_path}")
            
            # التحقق من حجم الملف
            file_size = os.path.getsize(temp_file_path)
            print(f"✅ حجم الملف المؤقت: {file_size} بايت")
            
            # حذف الملف المؤقت
            os.unlink(temp_file_path)
            
            if not os.path.exists(temp_file_path):
                print("✅ تم حذف الملف المؤقت بنجاح")
            else:
                print("❌ فشل في حذف الملف المؤقت")
                return False
        else:
            print("❌ فشل في إنشاء الملف المؤقت")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ اختبار الملفات المؤقتة - خطأ: {e}")
        return False

def test_environment_setup():
    """اختبار إعداد البيئة للملفات الكبيرة"""
    print("\n🔧 اختبار إعداد البيئة للملفات الكبيرة...")
    
    # التحقق من وجود الملفات المطلوبة
    required_files = [
        'telegram_drive_bot_large_files.py',
        'setup_local_bot_api.md',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - موجود")
        else:
            print(f"❌ {file} - مفقود")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_docker_availability():
    """اختبار توفر Docker"""
    print("\n🐳 اختبار توفر Docker...")
    
    try:
        import subprocess
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker متوفر: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker غير متوفر")
            return False
    except FileNotFoundError:
        print("❌ Docker غير مثبت")
        return False
    except Exception as e:
        print(f"❌ خطأ في فحص Docker: {e}")
        return False

def create_test_file(size_mb: int) -> str:
    """إنشاء ملف اختبار بحجم محدد"""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.test')
        
        # كتابة بيانات بالحجم المطلوب
        chunk_size = 1024 * 1024  # 1 ميجابايت
        data_chunk = b'A' * chunk_size
        
        for _ in range(size_mb):
            temp_file.write(data_chunk)
        
        temp_file.close()
        return temp_file.name
        
    except Exception as e:
        print(f"❌ فشل في إنشاء ملف الاختبار: {e}")
        return None

def test_large_file_simulation():
    """محاكاة التعامل مع ملف كبير"""
    print("\n📦 محاكاة التعامل مع ملف كبير...")
    
    try:
        # إنشاء ملف اختبار 50 ميجابايت
        print("📝 إنشاء ملف اختبار 50 ميجابايت...")
        test_file_path = create_test_file(50)
        
        if not test_file_path:
            return False
        
        # التحقق من حجم الملف
        file_size = os.path.getsize(test_file_path)
        expected_size = 50 * 1024 * 1024
        
        if abs(file_size - expected_size) < 1024:  # تسامح 1 كيلوبايت
            print(f"✅ تم إنشاء ملف بحجم {file_size / (1024*1024):.1f} ميجابايت")
        else:
            print(f"❌ حجم الملف غير صحيح: {file_size} بدلاً من {expected_size}")
            return False
        
        # محاكاة معالجة الملف
        print("⚙️ محاكاة معالجة الملف...")
        
        # قراءة الملف بأجزاء (محاكاة التنزيل)
        chunk_size = 8192
        total_read = 0
        
        with open(test_file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                total_read += len(chunk)
        
        if total_read == file_size:
            print(f"✅ تم قراءة الملف بالكامل: {total_read} بايت")
        else:
            print(f"❌ خطأ في قراءة الملف: {total_read} من {file_size}")
            return False
        
        # حذف ملف الاختبار
        os.unlink(test_file_path)
        print("✅ تم حذف ملف الاختبار")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في محاكاة الملف الكبير: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("🧪 بدء اختبار البوت مع دعم الملفات الكبيرة")
    print("=" * 60)
    
    tests = [
        ("استيراد المكتبات", test_imports),
        ("فئة البوت للملفات الكبيرة", test_large_files_bot_class),
        ("حدود أحجام الملفات", test_file_size_limits),
        ("التعامل مع الملفات المؤقتة", test_temp_file_handling),
        ("إعداد البيئة", test_environment_setup),
        ("توفر Docker", test_docker_availability),
        ("محاكاة ملف كبير", test_large_file_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} - خطأ غير متوقع: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 نتائج الاختبار: {passed}/{total} نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت!")
        print("\n📋 الخطوات التالية لدعم الملفات الكبيرة:")
        print("1. ثبت Docker على نظامك")
        print("2. احصل على API ID و API Hash من my.telegram.org")
        print("3. شغل خادم Bot API المحلي باستخدام Docker")
        print("4. أضف BOT_API_SERVER=http://localhost:8081 إلى ملف .env")
        print("5. شغل البوت باستخدام: python3 telegram_drive_bot_large_files.py")
        print("\n📖 راجع ملف setup_local_bot_api.md للتفاصيل الكاملة")
    else:
        print("❌ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه.")
        
        if passed >= total - 2:  # إذا نجح معظم الاختبارات
            print("\n💡 معظم الاختبارات نجحت. يمكنك المتابعة مع مراعاة الأخطاء البسيطة.")

if __name__ == '__main__':
    main()

