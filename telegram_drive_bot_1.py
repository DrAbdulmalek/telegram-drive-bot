#!/usr/bin/env python3
"""
بوت تيليجرام لرفع الملفات إلى Google Drive
يقوم برفع الملفات مباشرة من تيليجرام إلى Google Drive بدون تنزيلها محلياً
"""

import os
import io
import logging
from typing import Optional
import asyncio
import aiohttp

from telegram import Update, Document, PhotoSize, Video, Audio, Voice, VideoNote, Animation, Sticker
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramDriveBot:
    def __init__(self, telegram_token: str, google_credentials_file: str):
        """
        تهيئة البوت
        
        Args:
            telegram_token: رمز بوت التيليجرام
            google_credentials_file: مسار ملف بيانات اعتماد Google
        """
        self.telegram_token = telegram_token
        self.google_credentials_file = google_credentials_file
        self.drive_service = None
        self.user_credentials = {}
        
        # إعداد نطاقات Google Drive
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        welcome_message = """
🤖 مرحباً بك في بوت رفع الملفات إلى Google Drive!

📋 الأوامر المتاحة:
/start - عرض هذه الرسالة
/auth - ربط حسابك مع Google Drive
/status - عرض حالة الاتصال
/help - عرض المساعدة

📁 لرفع ملف، قم بإرسال أي ملف وسيتم رفعه تلقائياً إلى Google Drive الخاص بك.

⚠️ ملاحظة: يجب عليك أولاً ربط حسابك باستخدام الأمر /auth
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        help_message = """
📖 كيفية استخدام البوت:

1️⃣ ابدأ بالأمر /auth لربط حسابك مع Google Drive
2️⃣ اتبع الرابط المرسل وامنح الصلاحيات المطلوبة
3️⃣ أرسل رمز التفويض المستلم
4️⃣ ابدأ برفع الملفات بإرسالها مباشرة

📁 أنواع الملفات المدعومة:
• الصور (JPG, PNG, GIF, إلخ)
• الفيديوهات
• الملفات الصوتية
• المستندات
• أي نوع ملف آخر

🔒 الأمان:
• لا يتم حفظ ملفاتك على الخادم
• الرفع مباشر إلى Google Drive
• بياناتك محمية ومشفرة
        """
        await update.message.reply_text(help_message)
    
    async def auth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /auth لربط Google Drive"""
        user_id = update.effective_user.id
        
        try:
            # إنشاء رابط التفويض
            flow = Flow.from_client_secrets_file(
                self.google_credentials_file,
                scopes=self.SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            # حفظ flow للمستخدم
            self.user_credentials[user_id] = {'flow': flow}
            
            auth_message = f"""
🔗 لربط حسابك مع Google Drive:

1️⃣ اضغط على الرابط التالي:
{auth_url}

2️⃣ سجل دخولك إلى Google وامنح الصلاحيات
3️⃣ انسخ رمز التفويض المعروض
4️⃣ أرسل الرمز هنا في الدردشة

⏰ انتبه: الرابط صالح لمدة محدودة فقط
            """
            
            await update.message.reply_text(auth_message, disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رابط التفويض: {e}")
            await update.message.reply_text("❌ حدث خطأ في إنشاء رابط التفويض. حاول مرة أخرى.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /status لعرض حالة الاتصال"""
        user_id = update.effective_user.id
        
        if user_id in self.user_credentials and 'credentials' in self.user_credentials[user_id]:
            creds = self.user_credentials[user_id]['credentials']
            if creds and creds.valid:
                status_message = "✅ حسابك مربوط بنجاح مع Google Drive\n📁 يمكنك الآن رفع الملفات"
            else:
                status_message = "⚠️ انتهت صلاحية الاتصال. استخدم /auth للربط مجدداً"
        else:
            status_message = "❌ حسابك غير مربوط. استخدم /auth للربط مع Google Drive"
        
        await update.message.reply_text(status_message)
    
    async def handle_auth_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة رمز التفويض من المستخدم"""
        user_id = update.effective_user.id
        auth_code = update.message.text.strip()
        
        if user_id not in self.user_credentials or 'flow' not in self.user_credentials[user_id]:
            await update.message.reply_text("❌ لم يتم العثور على طلب تفويض. استخدم /auth أولاً")
            return
        
        try:
            flow = self.user_credentials[user_id]['flow']
            flow.fetch_token(code=auth_code)
            
            # حفظ بيانات الاعتماد
            credentials = flow.credentials
            self.user_credentials[user_id]['credentials'] = credentials
            
            # إزالة flow بعد الانتهاء
            del self.user_credentials[user_id]['flow']
            
            await update.message.reply_text("✅ تم ربط حسابك بنجاح! يمكنك الآن رفع الملفات.")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة رمز التفويض: {e}")
            await update.message.reply_text("❌ رمز التفويض غير صحيح. حاول مرة أخرى.")
    
    async def download_file_from_telegram(self, file_id: str, file_size: int) -> Optional[io.BytesIO]:
        """
        تنزيل ملف من تيليجرام إلى الذاكرة
        
        Args:
            file_id: معرف الملف في تيليجرام
            file_size: حجم الملف
            
        Returns:
            BytesIO object أو None في حالة الفشل
        """
        try:
            # الحد الأقصى لحجم الملف (20 ميجابايت)
            MAX_FILE_SIZE = 20 * 1024 * 1024
            
            if file_size > MAX_FILE_SIZE:
                return None
            
            # الحصول على رابط تنزيل الملف
            file_url = f"https://api.telegram.org/file/bot{self.telegram_token}/{file_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        file_data = await response.read()
                        return io.BytesIO(file_data)
                    else:
                        logger.error(f"فشل في تنزيل الملف: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"خطأ في تنزيل الملف: {e}")
            return None
    
    async def upload_to_drive(self, file_data: io.BytesIO, filename: str, user_id: int) -> Optional[str]:
        """
        رفع ملف إلى Google Drive
        
        Args:
            file_data: بيانات الملف
            filename: اسم الملف
            user_id: معرف المستخدم
            
        Returns:
            رابط الملف في Drive أو None في حالة الفشل
        """
        try:
            if user_id not in self.user_credentials or 'credentials' not in self.user_credentials[user_id]:
                return None
            
            credentials = self.user_credentials[user_id]['credentials']
            
            # التحقق من صلاحية بيانات الاعتماد
            if not credentials.valid:
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    return None
            
            # إنشاء خدمة Drive
            service = build('drive', 'v3', credentials=credentials)
            
            # إعداد بيانات الملف
            file_metadata = {
                'name': filename,
                'parents': []  # يمكن تحديد مجلد معين هنا
            }
            
            # رفع الملف
            media = MediaIoBaseUpload(file_data, mimetype='application/octet-stream', resumable=True)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            return file.get('webViewLink')
            
        except HttpError as e:
            logger.error(f"خطأ في Google Drive API: {e}")
            return None
        except Exception as e:
            logger.error(f"خطأ في رفع الملف: {e}")
            return None
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الملفات المرسلة"""
        user_id = update.effective_user.id
        
        # التحقق من ربط الحساب
        if user_id not in self.user_credentials or 'credentials' not in self.user_credentials[user_id]:
            await update.message.reply_text("❌ يجب ربط حسابك أولاً باستخدام /auth")
            return
        
        # الحصول على معلومات الملف
        document = update.message.document
        if not document:
            await update.message.reply_text("❌ لم يتم العثور على ملف")
            return
        
        # التحقق من حجم الملف
        if document.file_size > 20 * 1024 * 1024:  # 20 ميجابايت
            await update.message.reply_text("❌ حجم الملف كبير جداً (الحد الأقصى 20 ميجابايت)")
            return
        
        try:
            # إرسال رسالة تحميل
            loading_message = await update.message.reply_text("📤 جاري رفع الملف...")
            
            # الحصول على معلومات الملف من تيليجرام
            file = await context.bot.get_file(document.file_id)
            
            # تنزيل الملف إلى الذاكرة
            file_data = await self.download_file_from_telegram(file.file_path, document.file_size)
            
            if not file_data:
                await loading_message.edit_text("❌ فشل في تنزيل الملف")
                return
            
            # رفع الملف إلى Drive
            drive_link = await self.upload_to_drive(file_data, document.file_name, user_id)
            
            if drive_link:
                success_message = f"""
✅ تم رفع الملف بنجاح!

📁 اسم الملف: {document.file_name}
📊 الحجم: {document.file_size / 1024:.1f} كيلوبايت
🔗 الرابط: {drive_link}
                """
                await loading_message.edit_text(success_message, disable_web_page_preview=True)
            else:
                await loading_message.edit_text("❌ فشل في رفع الملف إلى Google Drive")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الملف: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الملف")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الصور المرسلة"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_credentials or 'credentials' not in self.user_credentials[user_id]:
            await update.message.reply_text("❌ يجب ربط حسابك أولاً باستخدام /auth")
            return
        
        try:
            # الحصول على أكبر حجم للصورة
            photo = update.message.photo[-1]
            
            loading_message = await update.message.reply_text("📤 جاري رفع الصورة...")
            
            # الحصول على معلومات الملف
            file = await context.bot.get_file(photo.file_id)
            
            # تنزيل الصورة
            file_data = await self.download_file_from_telegram(file.file_path, photo.file_size)
            
            if not file_data:
                await loading_message.edit_text("❌ فشل في تنزيل الصورة")
                return
            
            # تحديد اسم الملف
            filename = f"photo_{photo.file_unique_id}.jpg"
            
            # رفع الصورة إلى Drive
            drive_link = await self.upload_to_drive(file_data, filename, user_id)
            
            if drive_link:
                success_message = f"""
✅ تم رفع الصورة بنجاح!

📁 اسم الملف: {filename}
📊 الحجم: {photo.file_size / 1024:.1f} كيلوبايت
🔗 الرابط: {drive_link}
                """
                await loading_message.edit_text(success_message, disable_web_page_preview=True)
            else:
                await loading_message.edit_text("❌ فشل في رفع الصورة إلى Google Drive")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الصورة: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الصورة")
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        application = Application.builder().token(self.telegram_token).build()
        
        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("auth", self.auth_command))
        application.add_handler(CommandHandler("status", self.status_command))
        
        # معالج رموز التفويض (نص عادي)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_auth_code))
        
        # معالجات الملفات
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # تشغيل البوت
        logger.info("بدء تشغيل البوت...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """الدالة الرئيسية"""
    # قراءة المتغيرات البيئية
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    google_credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    if not telegram_token:
        print("❌ خطأ: لم يتم تعيين TELEGRAM_BOT_TOKEN")
        return
    
    if not os.path.exists(google_credentials_file):
        print(f"❌ خطأ: ملف بيانات الاعتماد غير موجود: {google_credentials_file}")
        return
    
    # إنشاء وتشغيل البوت
    bot = TelegramDriveBot(telegram_token, google_credentials_file)
    bot.run()

if __name__ == '__main__':
    main()

