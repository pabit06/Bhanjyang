# Production Deployment Guide

## Database: PostgreSQL

For production environments, **PostgreSQL** is strongly recommended over SQLite due to its superior concurrency, data integrity, and feature set.

### Migration Steps

1.  **Install PostgreSQL** on your server.
2.  **Create Database**:
    ```sql
    CREATE DATABASE bhanjyang_db;
    CREATE USER bhanjyang_user WITH PASSWORD 'strong_password';
    ALTER ROLE bhanjyang_user SET client_encoding TO 'utf8';
    ALTER ROLE bhanjyang_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE bhanjyang_user SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE bhanjyang_db TO bhanjyang_user;
    ```
3.  **Install Adapter**: Ensure `psycopg2-binary` is in your `requirements.txt` (already present).
4.  **Update Configuration**:
    Set the following environment variables in your production `.env` file:
    ```ini
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=bhanjyang_db
    DB_USER=bhanjyang_user
    DB_PASSWORD=strong_password
    DB_HOST=localhost
    DB_PORT=5432
    ```

## Caching: Redis

We use **Redis** for caching, session storage, and Celery task queue handling.

-   **Backend**: `django_redis.cache.RedisCache`
-   **Dependencies**: `django-redis`
-   **Configuration**:
    The system expects Redis to be available at `redis://localhost:6379/1` by default. You can override this via the `REDIS_URL` environment variable.

## Static Files

We use **WhiteNoise** for serving static files in production.

-   **Storage**: `whitenoise.storage.CompressedManifestStaticFilesStorage`
-   **Compression**: Gzip and Brotli compression are enabled automatically.
-   **Caching**: Long-term caching headers are set for versioned files.

### Deployment Checklist

-   [ ] `DEBUG=False` in `.env`
-   [ ] `SECRET_KEY` is a long, random string
-   [ ] `ALLOWED_HOSTS` includes your domain name
-   [ ] Database migrated: `python manage.py migrate`
-   [ ] Static files collected: `python manage.py collectstatic`
