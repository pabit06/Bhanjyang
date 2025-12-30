# Production Deployment Guide

Step-by-step guide for deploying Bhanjyang Cooperative to production.

## Prerequisites

- Ubuntu 20.04+ or Debian 11+ server
- Root or sudo access
- Domain name configured
- SSH access to server

## Production Requirements Overview

### Database: PostgreSQL

For production environments, **PostgreSQL** is strongly recommended over SQLite due to its superior concurrency, data integrity, and feature set.

### Caching: Redis

We use **Redis** for caching, session storage, and Celery task queue handling.

- **Backend**: `django_redis.cache.RedisCache`
- **Dependencies**: `django-redis`
- **Configuration**: The system expects Redis to be available at `redis://localhost:6379/1` by default. You can override this via the `REDIS_URL` environment variable.

### Security: Admin 2FA

Two-Factor Authentication (2FA) is enabled for the Django Admin interface.

- **Setup**: On first login, admins will be prompted to scan a QR code with an authenticator app (Google Authenticator, Authy, etc.).
- **Backup Codes**: Ensure admins save their backup codes in a secure location.
- **Enforcement**: By default, `OTE_ADMIN_2FA_REQUIRED` is set to `True` (via middleware or settings logic).

### Static Files

We use **WhiteNoise** for serving static files in production.

- **Storage**: `whitenoise.storage.CompressedManifestStaticFilesStorage`
- **Compression**: Gzip and Brotli compression are enabled automatically.
- **Caching**: Long-term caching headers are set for versioned files.

## Step 1: Server Setup

### Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Packages
```bash
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git
```

## Step 2: Database Setup

### Create PostgreSQL Database
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE bhanjyang_coop;
CREATE USER bhanjyang_user WITH PASSWORD 'secure_password';
ALTER ROLE bhanjyang_user SET client_encoding TO 'utf8';
ALTER ROLE bhanjyang_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bhanjyang_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bhanjyang_coop TO bhanjyang_user;
\q
```

**Install Adapter**: Ensure `psycopg2-binary` is in your `requirements.txt` (already present).

**Update Configuration**: Set the following environment variables in your production `.env` file:
```ini
DB_ENGINE=django.db.backends.postgresql
DB_NAME=bhanjyang_coop
DB_USER=bhanjyang_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

## Step 3: Application Setup

### Clone Repository
```bash
cd /var/www
sudo git clone https://github.com/yourusername/bhanjyang.git
sudo chown -R $USER:$USER bhanjyang
cd bhanjyang
```

### Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment
```bash
cp env.template .env
nano .env
```

Set production values:
- `DEBUG=False`
- `SECRET_KEY=your-secret-key`
- Database credentials
- Allowed hosts

### Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Step 4: Gunicorn Setup

### Install Gunicorn
```bash
pip install gunicorn
```

### Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/bhanjyang.service
```

```ini
[Unit]
Description=Bhanjyang Cooperative Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/bhanjyang
ExecStart=/var/www/bhanjyang/.venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/var/www/bhanjyang/bhanjyang.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Start Service
```bash
sudo systemctl start bhanjyang
sudo systemctl enable bhanjyang
```

## Step 5: Nginx Configuration

See [nginx.md](./nginx.md) for detailed Nginx configuration.

## Step 6: SSL Setup

See [ssl.md](./ssl.md) for SSL/TLS certificate setup.

## Step 7: Monitoring

See [monitoring.md](./monitoring.md) for monitoring and logging setup.

## Maintenance Commands

### Restart Application
```bash
sudo systemctl restart bhanjyang
```

### View Logs
```bash
sudo journalctl -u bhanjyang -f
```

### Update Application
```bash
cd /var/www/bhanjyang
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart bhanjyang
```

## Backup Strategy

### Database Backup
```bash
pg_dump -U bhanjyang_user bhanjyang_coop > backup_$(date +%Y%m%d).sql
```

### Media Files Backup
```bash
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

## Troubleshooting

### Check Gunicorn Status
```bash
sudo systemctl status bhanjyang
```

### Check Nginx Status
```bash
sudo systemctl status nginx
```

### Check Logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u bhanjyang -n 50
```

## Deployment Checklist

Before going live, ensure all items are checked:

- [ ] `DEBUG=False` in `.env`
- [ ] `SECRET_KEY` is a long, random string
- [ ] `ALLOWED_HOSTS` includes your domain name
- [ ] PostgreSQL database configured and migrated: `python manage.py migrate`
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Redis service running and accessible
- [ ] SSL/HTTPS configured
- [ ] Gunicorn service running
- [ ] Nginx configured and running
- [ ] Email backend configured (if using real emails)
- [ ] Monitoring and logging set up
- [ ] Backup strategy implemented

