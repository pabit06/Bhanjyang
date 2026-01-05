# News Events Management Commands - Deployment Guide
# (प्रबन्धन आदेशहरू - तैनाती गाइड)

## 📋 Overview (अवलोकन)

Management commands are Python files that are **automatically included** when you deploy your Django application to the server. They become available as `python manage.py <command_name>` commands.

**Management commands** भनेको Python files हुन् जुन Django application server मा deploy गर्दा **स्वचालित रूपमा समावेश** हुन्छन्। तिनीहरू `python manage.py <command_name>` commands को रूपमा उपलब्ध हुन्छन्।

---

## ✅ What Gets Deployed (के deploy हुन्छ)

### Files Included:
- ✅ All `.py` files in `apps/news_events/management/commands/`
- ✅ `__init__.py` files
- ✅ Command files are part of the codebase

### Files NOT Included:
- ❌ `__pycache__/` directories (auto-generated)
- ❌ `.pyc` files (compiled Python, auto-generated)

---

## 🚀 How to Use on Server (Server मा कसरी प्रयोग गर्ने)

### 1. **Manual Execution (म्यानुअल रूपमा)**

```bash
# SSH into your server
ssh user@your-server.com

# Navigate to project directory
cd /path/to/your/project

# Activate virtual environment (if using)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Run commands
python manage.py seed_news_events
python manage.py cleanup_old_content --days 365 --archive
python manage.py clear_cache --all
python manage.py export_content --format json --output backup.json
```

### 2. **Cron Jobs (Automated Tasks) (स्वचालित कार्यहरू)**

Set up cron jobs for regular maintenance:

```bash
# Edit crontab
crontab -e

# Examples:
# Cleanup old content every month (1st day at 2 AM)
0 2 1 * * cd /path/to/project && /path/to/venv/bin/python manage.py cleanup_old_content --days 365 --archive

# Clear cache every day at 3 AM
0 3 * * * cd /path/to/project && /path/to/venv/bin/python manage.py clear_cache --all

# Generate analytics report weekly (Monday at 6 AM)
0 6 * * 1 cd /path/to/project && /path/to/venv/bin/python manage.py news_analytics --days 7 --output file --file /path/to/reports/weekly_analytics.json

# Update view counts daily at 4 AM
0 4 * * * cd /path/to/project && /path/to/venv/bin/python manage.py update_view_counts
```

### 3. **Docker/Container Deployment (Docker मा)**

If using Docker, commands run inside the container:

```bash
# Run command in running container
docker exec -it your-container-name python manage.py seed_news_events

# Or in docker-compose
docker-compose exec web python manage.py cleanup_old_content --days 365 --archive
```

### 4. **CI/CD Pipeline (Automated Deployment)**

Add commands to your deployment script:

```yaml
# Example: .github/workflows/deploy.yml
- name: Run post-deployment commands
  run: |
    python manage.py clear_cache --all
    python manage.py update_view_counts
```

---

## 📝 Production Best Practices (Production मा Best Practices)

### 1. **Always Use Dry-Run First (पहिले Dry-Run प्रयोग गर्नुहोस्)**

```bash
# Test before actual execution
python manage.py cleanup_old_content --days 365 --archive --dry-run
python manage.py bulk_publish --action publish --category general --dry-run
```

### 2. **Backup Before Critical Operations (महत्वपूर्ण कार्यहरू अघि Backup)**

```bash
# Export data before cleanup
python manage.py export_content --format json --output backup_before_cleanup.json

# Then run cleanup
python manage.py cleanup_old_content --days 365 --archive
```

### 3. **Use Transactions (Database Safety) (Database सुरक्षा)**

Most commands use `@transaction.atomic` for safety, but always verify:

```bash
# Commands with transaction safety:
- cleanup_old_content.py ✅
- bulk_publish.py ✅
- newsletter_send.py ✅
- update_view_counts.py ✅
```

### 4. **Monitor Command Execution (Command Execution Monitor गर्नुहोस्)**

```bash
# Log output to file
python manage.py news_analytics --days 30 --output file --file /var/log/news_analytics.json

# Or redirect to log file
python manage.py cleanup_old_content --days 365 --archive >> /var/log/cleanup.log 2>&1
```

### 5. **Set Appropriate Permissions (उचित Permissions सेट गर्नुहोस्)**

```bash
# Ensure commands are executable
chmod +x manage.py

# Set proper file permissions
chmod 644 apps/news_events/management/commands/*.py
```

---

## 🔒 Security Considerations (सुरक्षा विचारहरू)

### 1. **Restrict Access (पहुँच सीमित गर्नुहोस्)**

- Only allow trusted users to run commands
- Use proper authentication on server
- Log all command executions

### 2. **Sensitive Commands (संवेदनशील Commands)**

Commands that modify data should be restricted:

```bash
# Dangerous commands - use with caution:
- cleanup_old_content.py --delete  # Deletes data permanently
- bulk_publish.py  # Changes content status
- newsletter_send.py  # Sends emails
```

### 3. **Environment Variables (Environment Variables)**

Use environment variables for sensitive data:

```bash
# In production, use .env file
export DATABASE_URL=postgresql://...
export SECRET_KEY=...
export EMAIL_HOST=...
```

---

## 📊 Recommended Cron Schedule (सुझावित Cron Schedule)

```bash
# Daily tasks
0 3 * * *  # 3 AM - Clear cache
0 4 * * *  # 4 AM - Update view counts

# Weekly tasks
0 6 * * 1  # Monday 6 AM - Generate analytics report

# Monthly tasks
0 2 1 * *  # 1st of month 2 AM - Cleanup old content
```

---

## 🛠️ Troubleshooting (समस्या समाधान)

### Command Not Found Error

```bash
# Ensure you're in the project directory
cd /path/to/your/project

# Check if command exists
python manage.py help | grep news

# Verify file exists
ls -la apps/news_events/management/commands/
```

### Permission Denied

```bash
# Check file permissions
ls -l apps/news_events/management/commands/*.py

# Fix permissions if needed
chmod 644 apps/news_events/management/commands/*.py
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"

# Verify Django can find the app
python manage.py shell
>>> from apps.news_events.management.commands import cleanup_old_content
```

---

## 📚 Command Reference (Command सन्दर्भ)

### Core Commands
- `seed_news_events` - Seed demo data
- `fix_empty_slugs` - Fix empty slugs
- `monitor_news` - System monitoring
- `news_analytics` - Analytics reports

### Content Management
- `cleanup_old_content` - Archive/delete old content
- `bulk_publish` - Bulk operations
- `export_content` - Export data

### Maintenance
- `clear_cache` - Cache management
- `update_view_counts` - Sync view counts
- `newsletter_send` - Send newsletters

---

## ✅ Summary (सारांश)

1. **Commands ARE deployed** - They're part of the codebase ✅
2. **They don't run automatically** - Must be executed manually or via cron ⚠️
3. **Use dry-run first** - Test before production execution 🧪
4. **Set up cron jobs** - Automate regular maintenance tasks ⏰
5. **Monitor execution** - Log all command outputs 📊
6. **Backup before critical operations** - Safety first 💾

---

**Last Updated:** 2025-01-05

