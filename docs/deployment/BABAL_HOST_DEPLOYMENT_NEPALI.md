# Babal.host मा Website Deploy गर्ने Guide (नेपाली)

## 📋 Overview

यो guide मा तपाईंको Django website लाई **babal.host** को Python Pro plan मा deploy गर्ने step-by-step process छ।

**Babal.host Features:**
- ✅ cPanel control panel
- ✅ Python Selector (Python environment management)
- ✅ LiteSpeed Webserver
- ✅ Free SSL certificate
- ✅ PostgreSQL/MySQL database support
- ✅ 2GB RAM (Pro plan)
- ✅ Unlimited websites, disk, bandwidth
- ✅ 30-day incremental backups

---

## 🎯 Pre-Deployment Checklist

### 1. Code तयारी
- [ ] सबै tests pass भएको छ
- [ ] Git मा सबै changes commit गरिएको छ
- [ ] Production settings file (`config/production.py`) तयार छ
- [ ] `.env` file template (`env.template`) मा सबै variables छन्
- [ ] `requirements.txt` file updated छ

### 2. Babal.host Account
- [ ] Python Pro plan purchase गरिसक्नुभएको छ
- [ ] cPanel access credentials छन्
- [ ] Domain name configured छ (यदि custom domain use गर्नुहुन्छ भने)

---

## 🚀 Step 1: cPanel मा Login गर्नुहोस्

1. **Babal.host client area** मा login गर्नुहोस्
2. **cPanel** access गर्नुहोस्
3. **Python Selector** tool खोल्नुहोस्

---

## 🐍 Step 2: Python Environment Setup

### Python Selector मा Setup:

1. **Python Selector** मा जानुहोस् (cPanel मा)
2. **Python Version Select गर्नुहोस्:**
   - Python 3.11 वा 3.12 select गर्नुहोस्
   - **⚠️ Important:** Python 3.11+ required छ

3. **Application Root Setup:**
   - Application root directory select गर्नुहोस्
   - Example: `public_html/bhanjyang` वा `public_html`
   - **Note:** यो directory मा तपाईंको Django project हुनुपर्छ

4. **Application URL Setup:**
   - Application URL set गर्नुहोस्
   - Example: `/` (root) वा `/bhanjyang`

5. **Passenger File Setup:**
   - `passenger_wsgi.py` file create गर्नुपर्छ (Step 3 मा)

---

## 📁 Step 3: Project Files Upload गर्नुहोस्

### Option 1: Git से (Recommended)

```bash
# cPanel Terminal वा SSH access मा:
cd ~/public_html
git clone <your-repository-url> bhanjyang
cd bhanjyang
```

### Option 2: File Manager से

1. **cPanel File Manager** खोल्नुहोस्
2. `public_html` directory मा जानुहोस्
3. **Upload** button click गर्नुहोस्
4. Project files upload गर्नुहोस् (zip file extract गर्न सकिन्छ)

### Project Structure:

```
public_html/
└── bhanjyang/          # वा public_html/ directly
    ├── manage.py
    ├── requirements.txt
    ├── config/
    ├── apps/
    ├── static/
    ├── media/
    ├── .env            # Create गर्नुपर्छ
    └── passenger_wsgi.py  # Create गर्नुपर्छ
```

---

## 🔧 Step 4: passenger_wsgi.py File Create गर्नुहोस्

**File:** `public_html/bhanjyang/passenger_wsgi.py` (वा project root मा)

```python
import os
import sys
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Add project directory to Python path
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.production')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**⚠️ Important:**
- File name exactly `passenger_wsgi.py` हुनुपर्छ
- Project root directory मा हुनुपर्छ
- Python Selector मा यो file path specify गर्नुपर्छ

---

## 🔐 Step 5: Environment Variables Setup (.env file)

### cPanel File Manager मा `.env` file create गर्नुहोस्:

**File:** `public_html/bhanjyang/.env`

```env
# SECURITY (REQUIRED)
SECRET_KEY=<generate-strong-key-here>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-babal-host-domain.com

# DATABASE (REQUIRED - cPanel MySQL/PostgreSQL)
# Option 1: MySQL (cPanel मा common)
DB_NAME=your_cpanel_db_name
DB_USER=your_cpanel_db_user
DB_PASSWORD=your_cpanel_db_password
DB_HOST=localhost
DB_PORT=3306

# Option 2: PostgreSQL (यदि available छ भने)
# DB_NAME=your_cpanel_db_name
# DB_USER=your_cpanel_db_user
# DB_PASSWORD=your_cpanel_db_password
# DB_HOST=localhost
# DB_PORT=5432

# REDIS (Optional - यदि available छ भने)
# REDIS_URL=redis://localhost:6379/1

# EMAIL (REQUIRED)
SEND_REAL_EMAILS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@bhanjyangcoop.com
DEVELOPER_EMAIL=developer@bhanjyangcoop.com

# SECURITY (REQUIRED)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# MONITORING (Optional)
SENTRY_DSN=your-sentry-dsn-here
ENVIRONMENT=production
RELEASE_VERSION=1.0.0
```

### SECRET_KEY Generate गर्ने:

```bash
# Local machine वा cPanel Terminal मा:
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**⚠️ Security:** `.env` file permissions set गर्नुहोस् (600 - owner read/write only)

---

## 🗄️ Step 6: Database Setup (cPanel MySQL/PostgreSQL)

### MySQL Setup (Common):

1. **cPanel MySQL Databases** मा जानुहोस्
2. **Create Database:**
   - Database name: `bhanjyang_coop` (वा आफ्नो name)
   - Create button click गर्नुहोस्

3. **Create Database User:**
   - Username: `bhanjyang_user` (वा आफ्नो name)
   - Strong password generate गर्नुहोस्
   - Create User button click गर्नुहोस्

4. **Add User to Database:**
   - User र database select गर्नुहोस्
   - **ALL PRIVILEGES** select गर्नुहोस्
   - Make Changes button click गर्नुहोस्

5. **Database Credentials Note गर्नुहोस्:**
   - Full database name: `cpanel_username_dbname`
   - Full username: `cpanel_username_dbuser`
   - Password: (जुन generate गर्नुभयो)

### PostgreSQL Setup (यदि available छ भने):

1. **cPanel PostgreSQL Databases** मा जानुहोस्
2. Similar process follow गर्नुहोस्

### Database Settings Update:

`config/production.py` मा database settings check गर्नुहोस्:

```python
# MySQL के लागि
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
        },
    }
}
```

**⚠️ Important:** `requirements.txt` मा `mysqlclient` वा `pymysql` package add गर्नुपर्छ MySQL के लागि।

---

## 📦 Step 7: Dependencies Install (requirements.txt)

### cPanel Terminal वा SSH मा:

```bash
# Project directory मा जानुहोस्
cd ~/public_html/bhanjyang

# Virtual environment activate (यदि Python Selector use गर्नुहुन्छ भने, यो automatic हुन्छ)
# Python Selector automatically virtual environment manage गर्छ

# Dependencies install
pip3.11 install -r requirements.txt

# यदि MySQL use गर्नुहुन्छ भने:
pip3.11 install mysqlclient
# वा
pip3.11 install pymysql
```

### requirements.txt मा MySQL Support Add:

```txt
# MySQL support (यदि MySQL use गर्नुहुन्छ भने)
mysqlclient>=2.1.0
# वा
# pymysql>=1.0.0
```

---

## 🔄 Step 8: Database Migrations

### cPanel Terminal वा SSH मा:

```bash
cd ~/public_html/bhanjyang

# Migrations run
python3.11 manage.py migrate

# Superuser create
python3.11 manage.py createsuperuser

# Static files collect
python3.11 manage.py collectstatic --noinput
```

---

## 📁 Step 9: Static & Media Files Setup

### Static Files:

1. **Static files collect** (already done in Step 8)
2. **cPanel File Manager** मा `staticfiles` directory check गर्नुहोस्
3. **Permissions set:**
   - `staticfiles/` directory: 755
   - Files inside: 644

### Media Files:

1. **Media directory create:**
   ```bash
   mkdir -p ~/public_html/bhanjyang/media
   chmod 755 ~/public_html/bhanjyang/media
   ```

2. **cPanel File Manager** मा permissions set:
   - `media/` directory: 755
   - Subdirectories: 755

### .htaccess File (Static Files के लागि):

**File:** `public_html/bhanjyang/staticfiles/.htaccess`

```apache
<IfModule mod_headers.c>
    <FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
        Header set Cache-Control "public, max-age=31536000, immutable"
    </FilesMatch>
</IfModule>
```

---

## 🔒 Step 10: SSL Certificate Setup

### Free SSL (Let's Encrypt):

1. **cPanel SSL/TLS** मा जानुहोस्
2. **Let's Encrypt** section मा जानुहोस्
3. **Domain select** गर्नुहोस्
4. **Issue** button click गर्नुहोस्
5. SSL certificate automatically install हुन्छ

### Force HTTPS:

`.htaccess` file create गर्नुहोस् (यदि needed छ भने):

**File:** `public_html/bhanjyang/.htaccess`

```apache
# Force HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

**Note:** Django settings मा `SECURE_SSL_REDIRECT=True` already set छ।

---

## ⚙️ Step 11: Python Selector Configuration

### Final Setup:

1. **Python Selector** मा जानुहोस्
2. **Application settings verify गर्नुहोस्:**
   - Python version: 3.11+
   - Application root: `~/public_html/bhanjyang`
   - Application URL: `/` (वा आफ्नो path)
   - Passenger file: `passenger_wsgi.py`

3. **Save** button click गर्नुहोस्

4. **Restart application** (यदि option छ भने)

---

## 🔧 Step 12: Django Settings Update

### config/production.py मा Updates:

**⚠️ Important:** `config/production.py` file मा database settings update गर्नुपर्छ यदि MySQL use गर्नुहुन्छ भने।

#### Option 1: MySQL Use गर्न (Common for cPanel)

`config/production.py` file मा database section replace गर्नुहोस्:

```python
# Database Configuration (for MySQL - cPanel)
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
        'CONN_MAX_AGE': 600,
    }
}
```

#### Option 2: PostgreSQL Use गर्न (यदि available छ भने)

PostgreSQL यदि available छ भने, original settings use गर्न सकिन्छ:

```python
# Database Configuration (for PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}
```

### Other Settings (Static & Media):

```python
# Static files (cPanel के लागि)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ALLOWED_HOSTS
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

### MySQL Package Install:

`requirements.txt` मा MySQL support add गर्नुहोस्:

```txt
# MySQL support (cPanel के लागि)
mysqlclient>=2.1.0
```

**Note:** यदि `mysqlclient` install हुन सक्दैन भने, `pymysql` use गर्न सकिन्छ:

```txt
# Alternative MySQL support
pymysql>=1.0.0
```

र `config/production.py` मा add गर्नुहोस्:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## ✅ Step 13: Testing

### Website Test:

1. **Browser मा website खोल्नुहोस्:**
   - `https://yourdomain.com`
   - `https://yourdomain.com/admin/`

2. **Check गर्नुहोस्:**
   - [ ] Homepage load हुन्छ
   - [ ] Static files load हुन्छन्
   - [ ] Admin panel accessible छ
   - [ ] Forms work गर्छन्
   - [ ] SSL certificate valid छ

### Error Logs Check:

1. **cPanel Error Logs** मा जानुहोस्
2. **Recent errors** check गर्नुहोस्
3. **Django logs** check:
   ```bash
   tail -f ~/public_html/bhanjyang/logs/django.log
   ```

---

## 🔄 Step 14: Future Updates (Code Update गर्दा)

### Update Process:

```bash
# 1. cPanel Terminal वा SSH मा login
cd ~/public_html/bhanjyang

# 2. Code update (Git से)
git pull origin main

# 3. Dependencies update
pip3.11 install -r requirements.txt

# 4. Migrations
python3.11 manage.py migrate

# 5. Static files
python3.11 manage.py collectstatic --noinput

# 6. Python Selector मा restart (यदि needed छ भने)
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: 500 Internal Server Error

**Solution:**
```bash
# Error logs check
tail -f ~/logs/error_log

# Django settings check
python3.11 manage.py check --deploy

# Permissions check
chmod 644 passenger_wsgi.py
chmod 755 ~/public_html/bhanjyang
```

### Issue 2: Static Files Not Loading

**Solution:**
```bash
# Static files collect again
python3.11 manage.py collectstatic --noinput --clear

# Permissions fix
chmod -R 755 ~/public_html/bhanjyang/staticfiles
```

### Issue 3: Database Connection Error

**Solution:**
- `.env` file मा database credentials verify गर्नुहोस्
- cPanel MySQL Databases मा user permissions check गर्नुहोस्
- Database name format: `cpanel_username_dbname`

### Issue 4: Module Not Found Error

**Solution:**
```bash
# Dependencies install
pip3.11 install -r requirements.txt

# Python Selector मा correct Python version select गर्नुहोस्
```

### Issue 5: Permission Denied

**Solution:**
```bash
# File permissions fix
find ~/public_html/bhanjyang -type d -exec chmod 755 {} \;
find ~/public_html/bhanjyang -type f -exec chmod 644 {} \;

# .env file secure
chmod 600 ~/public_html/bhanjyang/.env
```

---

## 📊 Important Notes for Babal.host

### 1. File Paths:
- Project root: `~/public_html/bhanjyang` वा `~/public_html`
- Static files: `~/public_html/bhanjyang/staticfiles`
- Media files: `~/public_html/bhanjyang/media`

### 2. Python Selector:
- Automatic virtual environment management
- Passenger file required (`passenger_wsgi.py`)
- Application restart through cPanel

### 3. Database:
- MySQL common छ (PostgreSQL यदि available छ भने use गर्न सकिन्छ)
- Database name format: `cpanel_username_dbname`
- Localhost connection use गर्नुहोस्

### 4. Redis:
- यदि Redis available छैन भने, local memory cache use गर्नुहोस्
- `config/production.py` मा cache settings adjust गर्नुहोस्

### 5. Celery:
- Shared hosting मा Celery setup complex हुन सक्छ
- यदि needed छैन भने, disable गर्न सकिन्छ
- Background tasks के लागि alternatives consider गर्नुहोस्

---

## 🔒 Security Checklist

- [ ] `.env` file permissions: 600 (owner read/write only)
- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] SSL certificate installed
- [ ] Database credentials secure
- [ ] File upload permissions restricted
- [ ] Admin panel protected (2FA enabled)

---

## 📞 Support

### Babal.host Support:
- **24/7 Support:** cPanel मा support ticket
- **Documentation:** [babal.host documentation](https://babal.host)
- **Email:** Support email through client area

### Project Documentation:
- Main README: `README.md`
- Deployment docs: `docs/deployment/`
- Production checklist: `docs/deployment/PRODUCTION_DEPLOYMENT_CHECKLIST.md`

---

## ✅ Final Checklist

Before going live:

- [ ] Python Selector configured
- [ ] `passenger_wsgi.py` file created
- [ ] `.env` file configured
- [ ] Database created and migrated
- [ ] Dependencies installed
- [ ] Static files collected
- [ ] Media directory created
- [ ] SSL certificate installed
- [ ] Website tested
- [ ] Error logs checked
- [ ] Admin panel accessible
- [ ] Forms working
- [ ] Security settings verified

---

## 🎉 Congratulations!

यदि सबै steps complete भएको छ भने, तपाईंको website अब **babal.host** मा live छ! 🚀

**Website URL:** https://yourdomain.com  
**Admin Panel:** https://yourdomain.com/admin/

---

**Last Updated:** 2025-01-XX  
**Hosting Provider:** Babal.host Python Pro Plan  
**Status:** Ready for Deployment ✅
