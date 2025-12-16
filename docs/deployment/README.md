# Deployment Documentation

This directory contains deployment guides and configuration for the Bhanjyang Cooperative project.

## Structure

```
deployment/
├── README.md                # This file
├── production.md            # Production deployment guide
├── docker.md                # Docker deployment
├── nginx.md                 # Nginx configuration
├── ssl.md                   # SSL/TLS setup
└── monitoring.md            # Monitoring and logging
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

1. Read [production.md](./production.md) for production setup
2. Configure [nginx.md](./nginx.md) for web server
3. Set up [ssl.md](./ssl.md) for HTTPS
4. Configure [monitoring.md](./monitoring.md) for logging

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

