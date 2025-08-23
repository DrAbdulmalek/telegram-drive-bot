#!/usr/bin/env python3
"""
بوت تيليجرام لرفع الملفات إلى Google Drive - نسخة محدثة لدعم الملفات الكبيرة
يقوم برفع الملفات مباشرة من تيليجرام إلى Google Drive بدون تنزيلها محلياً
يدعم الملفات الكبيرة حتى 2 جيجابايت باستخدام Local Bot API Server
"""

import os
import io
import logging
from typing import Optional
import asyncio
import aiohttp
import tempfile
import shutil
from pathlib import Path

from telegram import Update, Document, PhotoSize, Video, Audio, Voice, VideoNote, Animation, Sticker
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramDriveBotLargeFiles:
    def __init__(self, telegram_token: str, google_credentials_file: str, bot_api_server: str = None):
        """
        تهيئة البوت
        
        Args:
            telegram_token: رمز بوت التيليجرام
            google_credentials_file: مسار ملف بيانات اعتماد Google
            bot_api_server: عنوان خادم Bot API المحلي (اختياري)
        """
        self.telegram_token = telegram_token
        self.google_credentials_file = google_credentials_file
        self.bot_api_server = bot_api_server or "https://api.telegram.org"
        self.drive_service = None
        self.user_credentials = {}
        
        # إعداد نطاقات Google Drive
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        # حدود الملفات
        self.MAX_FILE_SIZE_STANDARD = 20 * 1024 * 1024  # 20 ميجابايت (Bot API العادي)
        self.MAX_FILE_SIZE_LOCAL = 2 * 1024 * 1024 * 1024  # 2 جيجابايت (Local Bot API)
        
    def get_max_file_size(self):
        """الحصول على الحد الأقصى لحجم الملف حسب نوع الخادم"""
        if self.bot_api_server != "https://api.telegram.org":
            return self.MAX_FILE_SIZE_LOCAL
        return self.MAX_FILE_SIZE_STANDARD
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        max_size = self.get_max_file_size() / (1024 * 1024)
        server_type = "محلي" if self.bot_api_server != "https://api.telegram.org" else "عادي"
        
        welcome_message = f"""
🤖 مرحباً بك في بوت رفع الملفات إلى Google Drive!

📋 الأوامر المتاحة:
/start - عرض هذه الرسالة
/auth - ربط حسابك مع Google Drive
/status - عرض حالة الاتصال
/info - معلومات الخادم والحدود
/help - عرض المساعدة

📁 لرفع ملف، قم بإرسال أي ملف وسيتم رفعه تلقائياً إلى Google Drive الخاص بك.

⚙️ نوع الخادم: {server_type}
📊 الحد الأقصى للملف: {max_size:.0f} ميجابايت

⚠️ ملاحظة: يجب عليك أولاً ربط حسابك باستخدام الأمر /auth
        """
        await update.message.reply_text(welcome_message)
    
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /info لعرض معلومات الخادم"""
        max_size = self.get_max_file_size() / (1024 * 1024)
        server_type = "محلي (Local Bot API)" if self.bot_api_server != "https://api.telegram.org" else "عادي (Telegram Bot API)"
        
        info_message = f"""
ℹ️ معلومات الخادم والحدود:

🖥️ نوع الخادم: {server_type}
🌐 عنوان الخادم: {self.bot_api_server}
📊 الحد الأقصى للملف: {max_size:.0f} ميجابايت

📝 ملاحظات:
• الخادم العادي يدعم ملفات حتى 20 ميجابايت
• الخادم المحلي يدعم ملفات حتى 2 جيجابايت
• جميع الملفات يتم رفعها مباشرة إلى Google Drive
• لا يتم حفظ الملفات على الخادم
        """
        await update.message.reply_text(info_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        max_size = self.get_max_file_size() / (1024 * 1024)
        
        help_message = f"""
📖 كيفية استخدام البوت:

1️⃣ ابدأ بالأمر /auth لربط حسابك مع Google Drive
2️⃣ اتبع الرابط المرسل وامنح الصلاحيات المطلوبة
3️⃣ أرسل رمز التفويض المستلم
4️⃣ ابدأ برفع الملفات بإرسالها مباشرة

📁 أنواع الملفات المدعومة:
• الصور (JPG, PNG, GIF, إلخ)
• الفيديوهات (حتى {max_size:.0f} ميجابايت)
• الملفات الصوتية
• المستندات
• أي نوع ملف آخر

🔒 الأمان:
• لا يتم حفظ ملفاتك على الخادم
• الرفع مباشر إلى Google Drive
• بياناتك محمية ومشفرة

⚡ نصائح:
• للملفات الكبيرة، قد يستغرق الرفع وقتاً أطول
• تأكد من اتصال إنترنت مستقر
• يمكنك رفع عدة ملفات متتالية
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
    
    async def download_file_from_telegram(self, file_id: str, file_size: int, use_temp_file: bool = False) -> Optional[io.BytesIO]:
        """
        تنزيل ملف من تيليجرام
        
        Args:
            file_id: معرف الملف في تيليجرام
            file_size: حجم الملف
            use_temp_file: استخدام ملف مؤقت للملفات الكبيرة
            
        Returns:
            BytesIO object أو مسار الملف المؤقت
        """
        try:
            max_size = self.get_max_file_size()
            
            if file_size > max_size:
                logger.error(f"حجم الملف {file_size} يتجاوز الحد الأقصى {max_size}")
                return None
            
            # الحصول على رابط تنزيل الملف
            file_url = f"{self.bot_api_server}/file/bot{self.telegram_token}/{file_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        if use_temp_file and file_size > 50 * 1024 * 1024:  # 50 ميجابايت
                            # استخدام ملف مؤقت للملفات الكبيرة
                            temp_file = tempfile.NamedTemporaryFile(delete=False)
                            async for chunk in response.content.iter_chunked(8192):
                                temp_file.write(chunk)
                            temp_file.close()
                            return temp_file.name
                        else:
                            # تحميل في الذاكرة للملفات الصغيرة
                            file_data = await response.read()
                            return io.BytesIO(file_data)
                    else:
                        logger.error(f"فشل في تنزيل الملف: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"خطأ في تنزيل الملف: {e}")
            return None
    
    async def upload_to_drive(self, file_data, filename: str, user_id: int, file_size: int = None) -> Optional[str]:
        """
        رفع ملف إلى Google Drive
        
        Args:
            file_data: بيانات الملف أو مسار الملف المؤقت
            filename: اسم الملف
            user_id: معرف المستخدم
            file_size: حجم الملف
            
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
            
            # تحديد نوع الرفع حسب نوع البيانات
            if isinstance(file_data, str):  # مسار ملف مؤقت
                media = MediaFileUpload(file_data, resumable=True)
            else:  # BytesIO object
                media = MediaIoBaseUpload(file_data, mimetype='application/octet-stream', resumable=True)
            
            # رفع الملف مع دعم الرفع المتقطع للملفات الكبيرة
            request = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"رفع {int(status.progress() * 100)}% مكتمل")
            
            # تنظيف الملف المؤقت إذا كان موجوداً
            if isinstance(file_data, str) and os.path.exists(file_data):
                os.unlink(file_data)
            
            return response.get('webViewLink')
            
        except HttpError as e:
            logger.error(f"خطأ في Google Drive API: {e}")
            # تنظيف الملف المؤقت في حالة الخطأ
            if isinstance(file_data, str) and os.path.exists(file_data):
                os.unlink(file_data)
            return None
        except Exception as e:
            logger.error(f"خطأ في رفع الملف: {e}")
            # تنظيف الملف المؤقت في حالة الخطأ
            if isinstance(file_data, str) and os.path.exists(file_data):
                os.unlink(file_data)
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
        max_size = self.get_max_file_size()
        if document.file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            await update.message.reply_text(f"❌ حجم الملف كبير جداً (الحد الأقصى {max_size_mb:.0f} ميجابايت)")
            return
        
        try:
            # إرسال رسالة تحميل
            loading_message = await update.message.reply_text("📤 جاري رفع الملف...")
            
            # الحصول على معلومات الملف من تيليجرام
            file = await context.bot.get_file(document.file_id)
            
            # تحديد ما إذا كان يجب استخدام ملف مؤقت
            use_temp_file = document.file_size > 50 * 1024 * 1024  # 50 ميجابايت
            
            # تنزيل الملف
            file_data = await self.download_file_from_telegram(
                file.file_path, 
                document.file_size, 
                use_temp_file
            )
            
            if not file_data:
                await loading_message.edit_text("❌ فشل في تنزيل الملف")
                return
            
            # تحديث رسالة التحميل
            await loading_message.edit_text("☁️ جاري رفع الملف إلى Google Drive...")
            
            # رفع الملف إلى Drive
            drive_link = await self.upload_to_drive(
                file_data, 
                document.file_name, 
                user_id, 
                document.file_size
            )
            
            if drive_link:
                file_size_mb = document.file_size / (1024 * 1024)
                success_message = f"""
✅ تم رفع الملف بنجاح!

📁 اسم الملف: {document.file_name}
📊 الحجم: {file_size_mb:.2f} ميجابايت
🔗 الرابط: {drive_link}

💡 يمكنك الآن الوصول إلى الملف من Google Drive الخاص بك
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
            drive_link = await self.upload_to_drive(file_data, filename, user_id, photo.file_size)
            
            if drive_link:
                file_size_kb = photo.file_size / 1024
                success_message = f"""
✅ تم رفع الصورة بنجاح!

📁 اسم الملف: {filename}
📊 الحجم: {file_size_kb:.1f} كيلوبايت
🔗 الرابط: {drive_link}
                """
                await loading_message.edit_text(success_message, disable_web_page_preview=True)
            else:
                await loading_message.edit_text("❌ فشل في رفع الصورة إلى Google Drive")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الصورة: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الصورة")
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الفيديوهات المرسلة"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_credentials or 'credentials' not in self.user_credentials[user_id]:
            await update.message.reply_text("❌ يجب ربط حسابك أولاً باستخدام /auth")
            return
        
        try:
            video = update.message.video
            if not video:
                await update.message.reply_text("❌ لم يتم العثور على فيديو")
                return
            
            # التحقق من حجم الملف
            max_size = self.get_max_file_size()
            if video.file_size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                await update.message.reply_text(f"❌ حجم الفيديو كبير جداً (الحد الأقصى {max_size_mb:.0f} ميجابايت)")
                return
            
            loading_message = await update.message.reply_text("📤 جاري رفع الفيديو...")
            
            # الحصول على معلومات الملف
            file = await context.bot.get_file(video.file_id)
            
            # تحديد ما إذا كان يجب استخدام ملف مؤقت
            use_temp_file = video.file_size > 50 * 1024 * 1024  # 50 ميجابايت
            
            # تنزيل الفيديو
            file_data = await self.download_file_from_telegram(
                file.file_path, 
                video.file_size, 
                use_temp_file
            )
            
            if not file_data:
                await loading_message.edit_text("❌ فشل في تنزيل الفيديو")
                return
            
            # تحديث رسالة التحميل
            await loading_message.edit_text("☁️ جاري رفع الفيديو إلى Google Drive...")
            
            # تحديد اسم الملف
            filename = video.file_name or f"video_{video.file_unique_id}.mp4"
            
            # رفع الفيديو إلى Drive
            drive_link = await self.upload_to_drive(file_data, filename, user_id, video.file_size)
            
            if drive_link:
                file_size_mb = video.file_size / (1024 * 1024)
                duration = video.duration or 0
                success_message = f"""
✅ تم رفع الفيديو بنجاح!

📁 اسم الملف: {filename}
📊 الحجم: {file_size_mb:.2f} ميجابايت
⏱️ المدة: {duration} ثانية
🔗 الرابط: {drive_link}
                """
                await loading_message.edit_text(success_message, disable_web_page_preview=True)
            else:
                await loading_message.edit_text("❌ فشل في رفع الفيديو إلى Google Drive")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الفيديو: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الفيديو")
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق مع إعداد خادم Bot API المخصص
        if self.bot_api_server != "https://api.telegram.org":
            application = Application.builder().token(self.telegram_token).base_url(f"{self.bot_api_server}/bot").build()
        else:
            application = Application.builder().token(self.telegram_token).build()
        
        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("auth", self.auth_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("info", self.info_command))
        
        # معالج رموز التفويض (نص عادي)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_auth_code))
        
        # معالجات الملفات
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        
        # تشغيل البوت
        logger.info("بدء تشغيل البوت...")
        logger.info(f"خادم Bot API: {self.bot_api_server}")
        logger.info(f"الحد الأقصى للملف: {self.get_max_file_size() / (1024 * 1024):.0f} ميجابايت")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """الدالة الرئيسية"""
    # قراءة المتغيرات البيئية
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    google_credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    bot_api_server = os.getenv('BOT_API_SERVER', 'https://api.telegram.org')
    
    if not telegram_token:
        print("❌ خطأ: لم يتم تعيين TELEGRAM_BOT_TOKEN")
        return
    
    if not os.path.exists(google_credentials_file):
        print(f"❌ خطأ: ملف بيانات الاعتماد غير موجود: {google_credentials_file}")
        return
    
    # إنشاء وتشغيل البوت
    bot = TelegramDriveBotLargeFiles(telegram_token, google_credentials_file, bot_api_server)
    bot.run()

if __name__ == '__main__':
    main()

