# Deployment Documentation

This directory contains deployment guides and configuration for the Bhanjyang Cooperative project.

## Structure

```
deployment/
├── README.md                           # This file
├── BABAL_HOST_DEPLOYMENT_NEPALI.md    # Babal.host deployment guide (Nepali)
├── BABAL_HOST_QUICK_GUIDE_NEPALI.md   # Babal.host quick guide (Nepali)
├── DEPLOYMENT_GUIDE_NEPALI.md         # Complete VPS deployment guide (Nepali)
├── QUICK_DEPLOYMENT_CHECKLIST_NEPALI.md # Quick checklist (Nepali)
├── PRODUCTION_DEPLOYMENT_CHECKLIST.md  # Detailed production checklist
├── production.md                       # Production deployment guide
├── docker.md                           # Docker deployment
├── nginx.md                            # Nginx configuration
├── ssl.md                              # SSL/TLS setup
└── monitoring.md                       # Monitoring and logging
```

## Deployment Options

### 1. Traditional Server Deployment
- Linux server (Ubuntu/Debian recommended)
- Nginx as reverse proxy
- Gunicorn as WSGI server
- PostgreSQL database
- Redis for caching

### 2. Docker Deployment
- Docker Compose setup
- Containerized services
- Easy scaling and management

### 3. Cloud Platform Deployment
- AWS, Azure, or GCP
- Managed databases
- Auto-scaling capabilities

## Quick Start

### For Babal.host Users (बबल होस्ट)
1. **Start here:** [BABAL_HOST_DEPLOYMENT_NEPALI.md](./BABAL_HOST_DEPLOYMENT_NEPALI.md) - Complete babal.host deployment guide in Nepali
2. **Quick reference:** [BABAL_HOST_QUICK_GUIDE_NEPALI.md](./BABAL_HOST_QUICK_GUIDE_NEPALI.md) - Quick checklist for babal.host

### For Nepali Speakers (नेपाली) - VPS/Server
1. **Start here:** [DEPLOYMENT_GUIDE_NEPALI.md](./DEPLOYMENT_GUIDE_NEPALI.md) - Complete step-by-step guide in Nepali
2. **Quick reference:** [QUICK_DEPLOYMENT_CHECKLIST_NEPALI.md](./QUICK_DEPLOYMENT_CHECKLIST_NEPALI.md) - Quick checklist

### For English Speakers
1. Read [PRODUCTION_DEPLOYMENT_CHECKLIST.md](./PRODUCTION_DEPLOYMENT_CHECKLIST.md) for detailed checklist
2. Read [production.md](./production.md) for production setup
3. Configure [nginx.md](./nginx.md) for web server
4. Set up [ssl.md](./ssl.md) for HTTPS
5. Configure [monitoring.md](./monitoring.md) for logging

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Nginx (for production)
- SSL certificate (for HTTPS)

## Environment Variables

Required environment variables are documented in `env.template` in the project root.

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up SSL/TLS
- [ ] Configure database security
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure backup strategy

