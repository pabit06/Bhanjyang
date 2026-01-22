# Website Live गर्ने Step-by-Step Guide (नेपाली)

## 📋 Overview

यो guide मा तपाईंको website लाई production मा live गर्ने step-by-step process छ।

---

## 🎯 Pre-Deployment Checklist

### 1. Code तयारी
- [ ] सबै tests pass भएको छ
- [ ] Git मा सबै changes commit गरिएको छ
- [ ] Production settings file (`config/production.py`) तयार छ
- [ ] `.env` file template (`env.template`) मा सबै variables छन्

---

## 🚀 Step 1: Production Server Setup

### Server Requirements
- **OS:** Ubuntu 20.04+ वा Debian 11+
- **RAM:** कम्तिमा 2GB (4GB+ recommended)
- **Storage:** कम्तिमा 20GB
- **Python:** 3.11 वा बढी
- **PostgreSQL:** 15+
- **Redis:** 7+
- **Nginx:** Latest version

### Server मा Basic Setup

```bash
# 1. System update
sudo apt update && sudo apt upgrade -y

# 2. Python install
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. PostgreSQL install
sudo apt install postgresql postgresql-contrib -y

# 4. Redis install
sudo apt install redis-server -y

# 5. Nginx install
sudo apt install nginx -y

# 6. Git install (if not installed)
sudo apt install git -y
```

---

## 🔐 Step 2: Environment Variables Setup

### `.env` File बनाउनुहोस्

Production server मा project directory मा `.env` file बनाउनुहोस्:

```bash
cd /path/to/Bhanjyang
cp env.template .env
nano .env
```

### Required Variables (`.env` file मा):

```env
# SECURITY (REQUIRED - सुरक्षा)
SECRET_KEY=<strong-random-key-here>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip-address

# DATABASE (REQUIRED - PostgreSQL)
DB_NAME=bhanjyang_coop
DB_USER=bhanjyang_user
DB_PASSWORD=strong_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# REDIS (REQUIRED)
REDIS_URL=redis://localhost:6379/1

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

# MONITORING (RECOMMENDED)
SENTRY_DSN=your-sentry-dsn-here
ENVIRONMENT=production
RELEASE_VERSION=1.0.0
```

### SECRET_KEY Generate गर्ने:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**⚠️ IMPORTANT:** `.env` file लाई कहिल्यै git मा commit नगर्नुहोस्!

---

## 🗄️ Step 3: Database Setup (PostgreSQL)

### Database बनाउनुहोस्:

```bash
# PostgreSQL मा login
sudo -u postgres psql

# Database create गर्नुहोस्
CREATE DATABASE bhanjyang_coop;

# User create गर्नुहोस्
CREATE USER bhanjyang_user WITH PASSWORD 'your_secure_password';

# Permissions दिनुहोस्
GRANT ALL PRIVILEGES ON DATABASE bhanjyang_coop TO bhanjyang_user;
ALTER USER bhanjyang_user CREATEDB;

# Exit
\q
```

### Database Connection Test:

```bash
psql -U bhanjyang_user -d bhanjyang_coop -h localhost
```

---

## 📦 Step 4: Project Setup on Server

### Code Clone/Upload गर्नुहोस्:

```bash
# Option 1: Git से clone
cd /var/www
git clone <your-repository-url> Bhanjyang
cd Bhanjyang

# Option 2: यदि code already छ भने
cd /path/to/Bhanjyang
```

### Virtual Environment Setup:

```bash
# Virtual environment बनाउनुहोस्
python3.11 -m venv .venv

# Activate गर्नुहोस्
source .venv/bin/activate

# Dependencies install गर्नुहोस्
pip install --upgrade pip
pip install -r requirements.txt
```

### Production Settings Use गर्नुहोस्:

`manage.py` वा `config/wsgi.py` मा settings module change गर्नुहोस्:

```python
# config/wsgi.py मा
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.production')

application = get_wsgi_application()
```

### Database Migrations:

```bash
# Migrations run गर्नुहोस्
python manage.py migrate

# Superuser create गर्नुहोस्
python manage.py createsuperuser
```

### Static Files Collection:

```bash
# Static files collect गर्नुहोस्
python manage.py collectstatic --noinput
```

---

## 🔒 Step 5: SSL Certificate Setup (HTTPS)

### Let's Encrypt Install:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### SSL Certificate Get गर्नुहोस्:

```bash
# Domain name साथ certificate लिनुहोस्
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

**Note:** यो step लाई Nginx configuration पछि गर्नुहोस् (Step 7)।

---

## ⚙️ Step 6: Gunicorn Setup

### Gunicorn Install:

```bash
# Virtual environment activate गर्नुहोस्
source .venv/bin/activate

# Gunicorn install
pip install gunicorn
```

### Gunicorn Service Create गर्नुहोस्:

File: `/etc/systemd/system/bhanjyang.service`

```ini
[Unit]
Description=Bhanjyang Cooperative Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/Bhanjyang
Environment="PATH=/var/www/Bhanjyang/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.production"
ExecStart=/var/www/Bhanjyang/.venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/Bhanjyang/bhanjyang.sock \
    --timeout 120 \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Service Start गर्नुहोस्:

```bash
# Service enable गर्नुहोस्
sudo systemctl daemon-reload
sudo systemctl enable bhanjyang
sudo systemctl start bhanjyang

# Status check
sudo systemctl status bhanjyang
```

---

## 🌐 Step 7: Nginx Configuration

### Nginx Config File Create गर्नुहोस्:

File: `/etc/nginx/sites-available/bhanjyang`

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (Certbot automatically adds these)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # File upload size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/Bhanjyang/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/Bhanjyang/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://unix:/var/www/Bhanjyang/bhanjyang.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

### Nginx Enable गर्नुहोस्:

```bash
# Site enable गर्नुहोस्
sudo ln -s /etc/nginx/sites-available/bhanjyang /etc/nginx/sites-enabled/

# Default site disable (optional)
sudo rm /etc/nginx/sites-enabled/default

# Config test
sudo nginx -t

# Nginx reload
sudo systemctl reload nginx
```

---

## 🔄 Step 8: Redis Setup

### Redis Start गर्नुहोस्:

```bash
# Redis start
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test
redis-cli ping  # Should return: PONG
```

---

## ⚡ Step 9: Celery Setup (Background Tasks)

### Celery Worker Service:

File: `/etc/systemd/system/celery.service`

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/Bhanjyang
Environment="PATH=/var/www/Bhanjyang/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.production"
ExecStart=/var/www/Bhanjyang/.venv/bin/celery -A config worker \
    --loglevel=info \
    --logfile=/var/www/Bhanjyang/logs/celery.log \
    --pidfile=/var/www/Bhanjyang/celery.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Celery Beat Service:

File: `/etc/systemd/system/celery-beat.service`

```ini
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/Bhanjyang
Environment="PATH=/var/www/Bhanjyang/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.production"
ExecStart=/var/www/Bhanjyang/.venv/bin/celery -A config beat \
    --loglevel=info \
    --logfile=/var/www/Bhanjyang/logs/celery-beat.log
Restart=always

[Install]
WantedBy=multi-user.target
```

### Services Start गर्नुहोस्:

```bash
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl enable celery-beat
sudo systemctl start celery
sudo systemctl start celery-beat

# Status check
sudo systemctl status celery
sudo systemctl status celery-beat
```

---

## 🔥 Step 10: Firewall Configuration

### UFW Firewall Setup:

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Firewall enable
sudo ufw enable

# Status check
sudo ufw status
```

---

## ✅ Step 11: Pre-Launch Testing

### Testing Checklist:

```bash
# 1. Website load test
curl -I https://yourdomain.com

# 2. Static files test
curl -I https://yourdomain.com/static/css/main.css

# 3. Admin panel test
# Browser मा: https://yourdomain.com/admin/

# 4. Health check
curl https://yourdomain.com/health/

# 5. Database connection test
python manage.py dbshell

# 6. Redis test
redis-cli ping

# 7. Email test
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### Manual Testing:

- [ ] Homepage load हुन्छ
- [ ] सबै pages accessible छन्
- [ ] Forms submit हुन्छन्
- [ ] File uploads काम गर्छ
- [ ] Admin panel accessible छ
- [ ] 2FA login काम गर्छ
- [ ] Email sending काम गर्छ
- [ ] Static files load हुन्छन्
- [ ] Media files load हुन्छन्
- [ ] SSL certificate valid छ

---

## 📊 Step 12: Monitoring Setup (Optional but Recommended)

### Sentry Setup:

1. [sentry.io](https://sentry.io) मा account बनाउनुहोस्
2. Django project create गर्नुहोस्
3. DSN लिनुहोस्
4. `.env` file मा add गर्नुहोस्: `SENTRY_DSN=your-dsn-here`

---

## 💾 Step 13: Backup Strategy

### Database Backup Script:

File: `/var/www/Bhanjyang/scripts/backup.sh`

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="bhanjyang_coop"
DB_USER="bhanjyang_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

### Cron Job Setup:

```bash
# Crontab edit
crontab -e

# Daily backup at 2 AM
0 2 * * * /var/www/Bhanjyang/scripts/backup.sh
```

---

## 🚀 Step 14: Final Deployment Commands

### Code Update गर्दा (Future updates):

```bash
# 1. Code pull
cd /var/www/Bhanjyang
git pull origin main

# 2. Virtual environment activate
source .venv/bin/activate

# 3. Dependencies update
pip install -r requirements.txt

# 4. Migrations run
python manage.py migrate

# 5. Static files collect
python manage.py collectstatic --noinput

# 6. Services restart
sudo systemctl restart bhanjyang
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl reload nginx

# 7. Status check
sudo systemctl status bhanjyang
sudo systemctl status celery
sudo systemctl status nginx
```

---

## 📝 Quick Reference Commands

### Service Management:

```bash
# Gunicorn
sudo systemctl start bhanjyang
sudo systemctl stop bhanjyang
sudo systemctl restart bhanjyang
sudo systemctl status bhanjyang

# Celery
sudo systemctl start celery
sudo systemctl restart celery
sudo systemctl status celery

# Nginx
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo nginx -t

# Redis
sudo systemctl start redis-server
sudo systemctl status redis-server
```

### Logs View:

```bash
# Gunicorn logs
sudo journalctl -u bhanjyang -f

# Celery logs
tail -f /var/www/Bhanjyang/logs/celery.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django logs
tail -f /var/www/Bhanjyang/logs/django.log
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Permission Errors

```bash
# File permissions fix
sudo chown -R www-data:www-data /var/www/Bhanjyang
sudo chmod -R 755 /var/www/Bhanjyang
sudo chmod -R 775 /var/www/Bhanjyang/media
sudo chmod -R 775 /var/www/Bhanjyang/staticfiles
```

### Issue 2: Database Connection Error

```bash
# PostgreSQL connection check
sudo -u postgres psql -c "\l" | grep bhanjyang

# User permissions check
sudo -u postgres psql -c "\du" | grep bhanjyang
```

### Issue 3: Static Files Not Loading

```bash
# Static files collect again
python manage.py collectstatic --noinput --clear

# Nginx reload
sudo systemctl reload nginx
```

### Issue 4: SSL Certificate Issues

```bash
# Certificate renew
sudo certbot renew

# Nginx reload
sudo systemctl reload nginx
```

---

## 📞 Support & Resources

### Documentation:
- Main README: `README.md`
- Deployment docs: `docs/deployment/`
- Production checklist: `docs/deployment/PRODUCTION_DEPLOYMENT_CHECKLIST.md`

### Useful Links:
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Gunicorn Docs: https://docs.gunicorn.org/
- Nginx Docs: https://nginx.org/en/docs/

---

## ✅ Final Checklist

Before going live, ensure:

- [ ] `.env` file properly configured
- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] PostgreSQL database created and migrated
- [ ] Redis running
- [ ] SSL certificate installed
- [ ] Gunicorn service running
- [ ] Nginx configured and running
- [ ] Celery services running
- [ ] Firewall configured
- [ ] Backup strategy in place
- [ ] All tests passing
- [ ] Monitoring setup (Sentry)
- [ ] Email configuration tested

---

## 🎉 Congratulations!

यदि सबै steps complete भएको छ भने, तपाईंको website अब live छ! 🚀

**Website URL:** https://yourdomain.com  
**Admin Panel:** https://yourdomain.com/admin/

---

**Last Updated:** 2025-01-XX  
**Status:** Ready for Production Deployment ✅
