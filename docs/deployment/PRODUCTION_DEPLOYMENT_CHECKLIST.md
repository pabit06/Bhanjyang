# Production Deployment Checklist 🚀

**Status:** 🟡 **Ready for Deployment with Setup Required**

## ✅ Code is Production-Ready

Your codebase is ready! All critical fixes have been applied:
- ✅ Configuration files cleaned up
- ✅ Celery configuration fixed
- ✅ Docker configuration fixed
- ✅ Security middleware in place
- ✅ Production settings file exists

---

## 🔴 CRITICAL: Before Going Live

### 1. Environment Configuration (.env file)

**Create a `.env` file on your production server with these values:**

```bash
# SECURITY (REQUIRED)
SECRET_KEY=<generate-strong-random-key-here>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip-address

# DATABASE (REQUIRED - PostgreSQL)
DB_NAME=bhanjyang_coop
DB_USER=your_db_user
DB_PASSWORD=strong_secure_password
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

**⚠️ IMPORTANT:** 
- Generate a strong SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Never commit `.env` file to git!

---

### 2. Database Migration (SQLite → PostgreSQL)

**Current:** Using SQLite (development)  
**Required:** PostgreSQL (production)

```bash
# On production server:
# 1. Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. Create database
sudo -u postgres psql
CREATE DATABASE bhanjyang_coop;
CREATE USER bhanjyang_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE bhanjyang_coop TO bhanjyang_user;
\q

# 3. Update .env with database credentials

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser
```

---

### 3. Use Production Settings

**Update your deployment to use production settings:**

```bash
# Option 1: Set environment variable
export DJANGO_SETTINGS_MODULE=config.production

# Option 2: Update manage.py or wsgi.py
# Change: os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# To: os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.production')
```

---

### 4. Static Files Collection

```bash
python manage.py collectstatic --noinput
```

---

### 5. SSL/HTTPS Setup

**Required for production security:**

```bash
# Install Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

### 6. Server Setup (Gunicorn + Nginx)

#### Install Gunicorn
```bash
pip install gunicorn
```

#### Create Gunicorn Service
**File:** `/etc/systemd/system/bhanjyang.service`

```ini
[Unit]
Description=Bhanjyang Cooperative Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Bhanjyang
Environment="PATH=/path/to/Bhanjyang/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.production"
ExecStart=/path/to/Bhanjyang/.venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/path/to/Bhanjyang/bhanjyang.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Nginx Configuration
**File:** `/etc/nginx/sites-available/bhanjyang`

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /path/to/Bhanjyang/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/Bhanjyang/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/path/to/Bhanjyang/bhanjyang.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/bhanjyang /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 7. Redis Setup

```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test
redis-cli ping  # Should return PONG
```

---

### 8. Celery Setup (Background Tasks)

**Create Celery Service:** `/etc/systemd/system/celery.service`

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/Bhanjyang
Environment="PATH=/path/to/Bhanjyang/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.production"
ExecStart=/path/to/Bhanjyang/.venv/bin/celery -A config worker --loglevel=info --logfile=/path/to/Bhanjyang/logs/celery.log
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

**Create Celery Beat Service:** `/etc/systemd/system/celery-beat.service`

```ini
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/Bhanjyang
Environment="PATH=/path/to/Bhanjyang/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.production"
ExecStart=/path/to/Bhanjyang/.venv/bin/celery -A config beat --loglevel=info --logfile=/path/to/Bhanjyang/logs/celery-beat.log
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start services
sudo systemctl start celery
sudo systemctl start celery-beat
sudo systemctl enable celery
sudo systemctl enable celery-beat
```

---

## 🟡 RECOMMENDED: Before Going Live

### 9. Email Configuration Testing

```bash
# Test email sending
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### 10. Monitoring Setup (Sentry)

1. Create account at [sentry.io](https://sentry.io)
2. Create Django project
3. Get DSN
4. Add to `.env`: `SENTRY_DSN=your-dsn-here`

### 11. Backup Strategy

```bash
# Database backup script
#!/bin/bash
pg_dump -U bhanjyang_user bhanjyang_coop > /backups/db_$(date +%Y%m%d_%H%M%S).sql

# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/backup_script.sh
```

### 12. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable
```

---

## ✅ Pre-Launch Testing Checklist

Before going live, test:

- [ ] All pages load correctly
- [ ] Forms submit successfully
- [ ] File uploads work
- [ ] Email sending works
- [ ] Admin panel accessible
- [ ] 2FA works for admin
- [ ] API endpoints respond
- [ ] Static files load
- [ ] Media files load
- [ ] SSL certificate valid
- [ ] Health check endpoint works: `/health/`
- [ ] Database queries perform well
- [ ] Redis caching works
- [ ] Celery tasks execute

---

## 🚀 Quick Deployment Commands

```bash
# 1. Pull latest code
git pull origin main

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart services
sudo systemctl restart bhanjyang
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl reload nginx

# 7. Check status
sudo systemctl status bhanjyang
sudo systemctl status celery
sudo systemctl status nginx
```

---

## 📊 Deployment Status

### ✅ Ready Now:
- Code quality ✅
- Security configuration ✅
- Production settings ✅
- Docker support ✅

### ⚠️ Needs Setup:
- Environment variables (.env)
- PostgreSQL database
- SSL certificate
- Server configuration (Gunicorn + Nginx)
- Email configuration
- Redis setup
- Celery services

---

## 🎯 Summary

**Can you go live?** 

**Answer:** 🟡 **Almost!** Your code is ready, but you need to:

1. **Set up production server** (Ubuntu/Debian)
2. **Configure environment variables** (.env file)
3. **Set up PostgreSQL** database
4. **Install SSL certificate** (Let's Encrypt)
5. **Configure Gunicorn + Nginx**
6. **Set up Redis and Celery**

**Estimated Time:** 2-4 hours for initial setup

**Once these are done, you're ready to go live!** 🚀

---

## 📞 Need Help?

- Check `docs/deployment/` for detailed guides
- Review `PROJECT_IMPROVEMENTS.md` for code improvements
- Test in staging environment first!

---

**Last Updated:** 2025-01-XX  
**Status:** Code Ready ✅ | Infrastructure Setup Required ⚠️
