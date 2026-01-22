# Babal.host Quick Deployment Guide (नेपाली) ⚡

## 🚀 Quick Steps (30-60 minutes)

### 1️⃣ cPanel Setup (5 min)
- [ ] cPanel मा login
- [ ] **Python Selector** खोल्नुहोस्
- [ ] Python 3.11+ select गर्नुहोस्

### 2️⃣ Project Upload (10 min)
```bash
# Option 1: Git से (Terminal मा)
cd ~/public_html
git clone <your-repo-url> bhanjyang

# Option 2: File Manager से
# cPanel File Manager → Upload project files
```

### 3️⃣ passenger_wsgi.py Create (5 min)
**File:** `public_html/bhanjyang/passenger_wsgi.py`
```python
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 4️⃣ .env File Setup (5 min)
**File:** `public_html/bhanjyang/.env`
```env
SECRET_KEY=<generate-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# MySQL (cPanel)
DB_NAME=cpanel_username_dbname
DB_USER=cpanel_username_dbuser
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Email
SEND_REAL_EMAILS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### 5️⃣ Database Setup (5 min)
1. **cPanel → MySQL Databases**
2. Database create: `bhanjyang_coop`
3. User create: `bhanjyang_user`
4. User लाई database मा add गर्नुहोस् (ALL PRIVILEGES)
5. Credentials `.env` मा add गर्नुहोस्

### 6️⃣ Dependencies Install (5 min)
```bash
cd ~/public_html/bhanjyang
pip3.11 install -r requirements.txt
pip3.11 install mysqlclient  # MySQL के लागि
```

### 7️⃣ Migrations & Setup (5 min)
```bash
python3.11 manage.py migrate
python3.11 manage.py createsuperuser
python3.11 manage.py collectstatic --noinput
```

### 8️⃣ Python Selector Config (5 min)
1. **Python Selector** मा जानुहोस्
2. Application root: `~/public_html/bhanjyang`
3. Application URL: `/`
4. Passenger file: `passenger_wsgi.py`
5. Save & Restart

### 9️⃣ SSL Certificate (5 min)
1. **cPanel → SSL/TLS**
2. **Let's Encrypt** section
3. Domain select → **Issue**

### 🔟 Testing (5 min)
- [ ] https://yourdomain.com
- [ ] https://yourdomain.com/admin/
- [ ] Static files load
- [ ] Forms work

---

## 📋 Important Files

### passenger_wsgi.py
```
public_html/bhanjyang/passenger_wsgi.py
```

### .env
```
public_html/bhanjyang/.env
```

### .htaccess (Optional)
```
public_html/bhanjyang/.htaccess
```

---

## 🔧 MySQL Settings Update

### config/production.py मा:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### requirements.txt मा add:

```txt
mysqlclient>=2.1.0
```

---

## 🔄 Update Commands

```bash
cd ~/public_html/bhanjyang
git pull origin main
pip3.11 install -r requirements.txt
python3.11 manage.py migrate
python3.11 manage.py collectstatic --noinput
# Python Selector मा restart
```

---

## ⚠️ Common Issues

### 500 Error
```bash
# Logs check
tail -f ~/logs/error_log
# Permissions fix
chmod 644 passenger_wsgi.py
```

### Static Files Not Loading
```bash
python3.11 manage.py collectstatic --noinput --clear
chmod -R 755 staticfiles/
```

### Database Error
- `.env` मा credentials verify
- cPanel MySQL मा permissions check

---

## 📞 Help

- **Full Guide:** `docs/deployment/BABAL_HOST_DEPLOYMENT_NEPALI.md`
- **Babal.host Support:** cPanel support ticket
- **Project Docs:** `docs/deployment/`

---

**Time:** 30-60 minutes  
**Status:** Ready ✅
