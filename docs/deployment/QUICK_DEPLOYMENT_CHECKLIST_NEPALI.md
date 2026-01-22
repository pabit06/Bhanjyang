# Quick Deployment Checklist (नेपाली) ✅

## 🚀 Website Live गर्ने Quick Steps

### 1️⃣ Server Preparation (15-30 minutes)
```bash
# System update
sudo apt update && sudo apt upgrade -y

# Required packages install
sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server nginx git -y
```

### 2️⃣ Environment Setup (10 minutes)
```bash
# .env file बनाउनुहोस्
cd /var/www/Bhanjyang
cp env.template .env
nano .env  # Required values fill गर्नुहोस्

# SECRET_KEY generate
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Required .env values:**
- ✅ `SECRET_KEY` (strong random key)
- ✅ `DEBUG=False`
- ✅ `ALLOWED_HOSTS` (your domain)
- ✅ Database credentials (PostgreSQL)
- ✅ Redis URL
- ✅ Email settings
- ✅ SSL settings

### 3️⃣ Database Setup (10 minutes)
```bash
# PostgreSQL मा database create
sudo -u postgres psql
CREATE DATABASE bhanjyang_coop;
CREATE USER bhanjyang_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bhanjyang_coop TO bhanjyang_user;
\q
```

### 4️⃣ Project Setup (15 minutes)
```bash
# Virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Superuser
python manage.py createsuperuser

# Static files
python manage.py collectstatic --noinput
```

### 5️⃣ Gunicorn Setup (10 minutes)
```bash
# Service file create: /etc/systemd/system/bhanjyang.service
# (See full guide for config)

# Start service
sudo systemctl daemon-reload
sudo systemctl enable bhanjyang
sudo systemctl start bhanjyang
```

### 6️⃣ Nginx Setup (15 minutes)
```bash
# Config file create: /etc/nginx/sites-available/bhanjyang
# (See full guide for config)

# Enable site
sudo ln -s /etc/nginx/sites-available/bhanjyang /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7️⃣ SSL Certificate (10 minutes)
```bash
# Certbot install
sudo apt install certbot python3-certbot-nginx -y

# Certificate get
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 8️⃣ Redis & Celery (10 minutes)
```bash
# Redis start
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Celery services (see full guide for config files)
sudo systemctl enable celery celery-beat
sudo systemctl start celery celery-beat
```

### 9️⃣ Firewall (5 minutes)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 🔟 Testing (10 minutes)
- [ ] Website load: `curl -I https://yourdomain.com`
- [ ] Admin panel: `https://yourdomain.com/admin/`
- [ ] Health check: `https://yourdomain.com/health/`
- [ ] Static files load
- [ ] Forms work
- [ ] Email sending works

---

## 📋 Complete Checklist

### Before Deployment
- [ ] Code ready (all tests pass)
- [ ] Git repository up to date
- [ ] Production settings file exists
- [ ] `.env` template ready

### Server Setup
- [ ] Ubuntu/Debian server ready
- [ ] Python 3.11+ installed
- [ ] PostgreSQL installed
- [ ] Redis installed
- [ ] Nginx installed
- [ ] Git installed

### Configuration
- [ ] `.env` file created with all values
- [ ] `SECRET_KEY` generated (strong)
- [ ] `DEBUG=False`
- [ ] Database credentials set
- [ ] Email credentials set
- [ ] SSL settings configured

### Database
- [ ] PostgreSQL database created
- [ ] Database user created
- [ ] Permissions granted
- [ ] Migrations run
- [ ] Superuser created

### Application
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Production settings active
- [ ] Static files collected
- [ ] Media directory permissions set

### Services
- [ ] Gunicorn service configured
- [ ] Gunicorn service running
- [ ] Nginx configured
- [ ] Nginx running
- [ ] Redis running
- [ ] Celery worker running
- [ ] Celery beat running

### Security
- [ ] SSL certificate installed
- [ ] HTTPS redirect working
- [ ] Firewall configured
- [ ] Security headers set
- [ ] CSRF protection enabled

### Testing
- [ ] Homepage loads
- [ ] All pages accessible
- [ ] Forms work
- [ ] File uploads work
- [ ] Admin panel accessible
- [ ] 2FA works
- [ ] Email sending works
- [ ] Static files load
- [ ] Media files load
- [ ] API endpoints work

### Monitoring (Optional)
- [ ] Sentry configured
- [ ] Logging configured
- [ ] Backup strategy in place

---

## 🔄 Update Commands (Future Updates)

```bash
# Quick update script
cd /var/www/Bhanjyang
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart bhanjyang celery celery-beat
sudo systemctl reload nginx
```

---

## 🆘 Troubleshooting

### Service Not Starting
```bash
# Check status
sudo systemctl status bhanjyang

# Check logs
sudo journalctl -u bhanjyang -f
```

### Permission Issues
```bash
sudo chown -R www-data:www-data /var/www/Bhanjyang
sudo chmod -R 755 /var/www/Bhanjyang
```

### Database Connection Error
```bash
# Test connection
psql -U bhanjyang_user -d bhanjyang_coop -h localhost
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput --clear
sudo systemctl reload nginx
```

---

## 📞 Help

- Full Guide: `docs/deployment/DEPLOYMENT_GUIDE_NEPALI.md`
- Production Checklist: `docs/deployment/PRODUCTION_DEPLOYMENT_CHECKLIST.md`
- Deployment README: `docs/deployment/README.md`

---

**Estimated Total Time:** 2-4 hours  
**Status:** Ready to Deploy ✅
