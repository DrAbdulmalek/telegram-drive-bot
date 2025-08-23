#!/usr/bin/env python3
"""
سكريبت لرفع ملفات مشروع بوت تيليجرام إلى مستودع GitHub جديد.
"""

import os
import zipfile
import requests
import json
import base64

def create_github_repo(username, token, repo_name, description="Telegram Drive Bot project files"):
    """
    ينشئ مستودع GitHub جديد.
    """
    url = f"https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": False,  # يمكن تغييرها إلى True إذا أردت مستودع خاص
        "auto_init": False # لا تنشئ README.md تلقائيا
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✅ تم إنشاء المستودع '{repo_name}' بنجاح.")
        return True
    else:
        print(f"❌ فشل إنشاء المستودع: {response.status_code} - {response.json()}")
        return False

def upload_file_to_github(username, token, repo_name, file_path, github_path):
    """
    يرفع ملف إلى مستودع GitHub.
    """
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{github_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    data = {
        "message": f"Add {github_path}",
        "content": content
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✅ تم رفع الملف '{file_path}' إلى '{github_path}' بنجاح.")
        return True
    else:
        print(f"❌ فشل رفع الملف '{file_path}': {response.status_code} - {response.json()}")
        return False

def main():
    print("🚀 سكريبت رفع ملفات البوت إلى GitHub")
    print("=======================================")
    
    username = input("أدخل اسم مستخدم GitHub الخاص بك: ").strip()
    token = input("أدخل رمز الوصول الشخصي (Personal Access Token) لـ GitHub: ").strip()
    repo_name = input("أدخل اسم المستودع الجديد (مثال: telegram-drive-bot): ").strip()
    
    print("\n--- بدء العملية ---")
    
    # 1. إنشاء المستودع
    if not create_github_repo(username, token, repo_name):
        print("❌ فشل إنشاء المستودع. يرجى التحقق من اسم المستودع ورمز الوصول.")
        return
        
    # 2. قائمة الملفات للرفع
    files_to_upload = [
        "telegram_drive_bot_large_files.py",
        "requirements.txt",
        "Dockerfile",
        "start.sh",
        "LICENSE",
        "README.md",
        "SETUP_GUIDE.md",
        "LARGE_FILES_GUIDE.md",
        "docker-compose.yml",
        ".env.large.example",
        "setup_google_credentials.py",
        "test_large_files_bot.py",
        "credentials_template.json",
        ".gitignore"
    ]
    
    # 3. رفع الملفات
    for file_name in files_to_upload:
        local_path = os.path.join("/home/ubuntu", file_name)
        github_path = file_name # نفس الاسم في المستودع
        
        if os.path.exists(local_path):
            upload_file_to_github(username, token, repo_name, local_path, github_path)
        else:
            print(f"⚠️ الملف '{local_path}' غير موجود. سيتم تخطيه.")
            
    print("\n--- العملية اكتملت ---")
    print(f"🎉 تم رفع الملفات إلى المستودع: https://github.com/{username}/{repo_name}")
    print("\n⚠️ ملاحظة هامة: تأكد من أن رمز الوصول الشخصي (Personal Access Token) لديه صلاحيات 'repo' و 'workflow'.")
    print("لإنشاء رمز وصول شخصي: https://github.com/settings/tokens")

if __name__ == "__main__":
    main()

