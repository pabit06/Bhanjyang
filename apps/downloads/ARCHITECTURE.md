# Downloads App Architecture
# (Downloads App वास्तुकला)

**Version:** 1.0.0  
**Last Updated:** January 6, 2026

---

## 📐 Architecture Overview

The Downloads app follows a **layered architecture** pattern with clear separation of concerns:

1. **Presentation Layer** (Templates, Static Files)
2. **View Layer** (Views, URL routing)
3. **Service Layer** (Business logic)
4. **Security Layer** (Validation, scanning, access control)
5. **Performance Layer** (Caching, optimization, CDN)
6. **Data Layer** (Models, Database)

---

## 🏗️ Component Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        T1[download.html]
        T2[file_detail.html]
        JS[JavaScript]
        CSS[CSS]
    end
    
    subgraph "View Layer"
        V1[download_center_view]
        V2[download_file_view]
        V3[file_detail_view]
        V4[bulk_download_view]
        U[URLs]
    end
    
    subgraph "Service Layer"
        S1[DownloadsService]
        S2[FileDownloadService]
        S3[BulkDownloadService]
        S4[DownloadsAnalyticsService]
    end
    
    subgraph "Security Layer"
        SEC1[FileSecurityValidator]
        SEC2[VirusScanManager]
        SEC3[AccessControlManager]
        SEC4[SecurityAuditLogger]
    end
    
    subgraph "Performance Layer"
        P1[DownloadsCache]
        P2[DownloadsPerformanceMonitor]
        P3[DownloadsQueryOptimizer]
        P4[DownloadsCDNManager]
    end
    
    subgraph "Data Layer"
        M1[DownloadableFile Model]
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
        STORAGE[(File Storage)]
    end
    
    T1 --> V1
    T2 --> V3
    JS --> V2
    JS --> V4
    
    V1 --> S1
    V2 --> S2
    V3 --> S2
    V4 --> S3
    
    S1 --> P1
    S1 --> P3
    S2 --> SEC1
    S2 --> SEC3
    S3 --> SEC3
    S4 --> M1
    
    SEC1 --> SEC2
    
    M1 --> DB
    P1 --> CACHE
    M1 --> STORAGE
    
    P4 --> STORAGE
```

---

## 🔄 Data Flow Diagrams

### File Download Flow

```mermaid
sequenceDiagram
    participant User
    participant View
    participant Service
    participant Security
    participant Cache
    participant Model
    participant Storage
    
    User->>View: Request file download
    View->>Service: process_file_download()  
    Service->>Security: check_access_control()
    
    alt User not authenticated & login required
        Security-->>Service: Access Denied
        Service-->>View: Redirect to login
        View-->>User: Login page
    else Access granted
        Security-->>Service: Access OK
        Service->>Model: get file object
        Model->>Storage: get file URL
        Storage-->>Model: file URL
        Model-->>Service: file object
        Service->>Model: increment_download_count()
        Service->>Security: log_download()
        Service-->>View: file URL
        View-->>User: Redirect to file
    end
```

### File Upload Flow (Admin)

```mermaid
sequenceDiagram
    participant Admin
    participant Django Admin
    participant Model
    participant Security
    participant Scanner
    participant Storage
    
    Admin->>Django Admin: Upload file
    Django Admin->>Model: save()
    Model->>Security: validate_file_security()
    
    Security->>Security: check_extension()
    Security->>Security: check_size()
    Security->>Security: check_mime_type()
    
    alt Validation failed
        Security-->>Model: Validation errors
        Model-->>Django Admin: Error message
        Django Admin-->>Admin: Show errors
    else Validation passed
        Security->>Scanner: scan_for_virus()
        
        alt Virus detected
            Scanner-->>Security: Virus found
            Security-->>Model: Reject file
            Model-->>Django Admin: Security error
            Django Admin-->>Admin: Virus detected
        else File clean
            Scanner-->>Security: Clean
            Security->>Security: generate_file_hash()
            Security-->>Model: Validation OK + hash
            Model->>Storage: store file
            Storage-->>Model: file path
            Model->>Model: save to database
            Model-->>Django Admin: Success
            Django Admin-->>Admin: File uploaded
        end
    end
```

### Download Center Page Load Flow

```mermaid
sequenceDiagram
    participant User
    participant View
    participant Service
    participant Cache
    participant Model
    participant DB
    
    User->>View: GET /downloads/
    View->>Service: get_download_center_context()
    Service->>Cache: check cache
    
    alt Cache hit
        Cache-->>Service: cached data
    else Cache miss
        Service->>Model: get_filtered_files()
        Model->>DB: SELECT query (optimized)
        DB-->>Model: file records
        Model-->>Service: QuerySet
        Service->>Service: group_by_category()
        Service->>Cache: store in cache
    end
    
    Service-->>View: context data
    View-->>User: rendered HTML
```

---

## 🗂️ File Organization

```
apps/downloads/
├── __init__.py
├── admin.py              # Django admin configuration
├── apps.py               # App configuration
├── models.py             # Data models (DownloadableFile)
├── views.py              # View functions
├── urls.py               # URL routing
├── forms.py              # Forms (if any)
│
├── services.py           # Business logic services
├── security.py           # Security features
├── performance.py        # Performance optimizations
├── utils/                # Utility functions
│   ├── __init__.py
│   └── helpers.py
│
├── management/           # Management commands
│   └── commands/
│       ├── cleanup_expired_files.py
│       └── generate_download_stats.py
│
├── migrations/           # Database migrations
├── tests/                # Test suite
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_services.py
│   ├── test_security.py
│   └── test_performance.py
│
├── static/downloads/     # Static files
│   ├── css/
│   │   └── downloads.css
│   └── js/
│       └── downloads.js
│
├── templates/downloads/  # Templates
│   ├── download.html
│   ├── file_detail.html
│   └── partials/
│       ├── file_card.html
│       └── category_section.html
│
└── README.md             # This file
```

---

## 🔐 Security Architecture

### Security Layers

```mermaid
graph TB
    A[User Request] --> B{IP Blacklist Check}
    B -->|Blacklisted| C[403 Forbidden]
    B -->|OK| D{Rate Limit Check}
    D -->|Exceeded| E[429 Too Many Requests]
    D -->|OK| F{Authentication Check}
    F -->|Required & Not Auth| G[Redirect to Login]
    F -->|OK| H{File Security Check}
    H -->|Invalid| I[400 Bad Request]
    H -->|OK| J{Virus Scan}
    J -->|Infected| K[403 Forbidden + Log]
    J -->|Clean| L{Expiration Check}
    L -->|Expired| M[410 Gone]
    L -->|Valid| N[Serve File + Log]
    N --> O[Audit Trail]
```

### Security Components

```mermaid
classDiagram
    class FileSecurityValidator {
        +validate_file_security(file)
        +check_file_extension(file)
        +check_file_size(file)
        +check_mime_type(file)
        +generate_file_hash(file)
    }
    
    class VirusScanManager {
        +scan_file(file_path)
        +is_clamav_available()
        +quarantine_file(file_path)
    }
    
    class AccessControlManager {
        +check_user_permission(user, file)
        +check_login_required(file)
        +check_expiration(file)
        +log_access_attempt(user, file, success)
    }
    
    class SecurityAuditLogger {
        +log_download(user, file)
        +log_failed_access(user, file, reason)
        +log_virus_detection(file)
        +log_security_violation(user, action)
    }
    
    FileSecurityValidator --> VirusScanManager
    AccessControlManager --> SecurityAuditLogger
```

---

## ⚡ Performance Architecture

### Caching Strategy

```mermaid
graph LR
    A[Request] --> B{Check Cache}
    B -->|Hit| C[Return Cached Data]
    B -->|Miss| D[Query Database]
    D --> E[Process Data]
    E --> F[Store in Cache]
    F --> G[Return Data]
    
    C --> H[Fast Response ~10ms]
    G --> I[Slower Response ~100ms]
```

### Cache Layers

```mermaid
graph TB
    subgraph "Application Cache (Redis)"
        C1[Download Center Context]
        C2[File Listings]
        C3[Category Groups]
        C4[Statistics]
    end
    
    subgraph "Database Query Cache"
        Q1[Filtered QuerySets]
        Q2[Count Queries]
        Q3[Aggregations]
    end
    
    subgraph "CDN Cache"
        CDN1[Static Files]
        CDN2[File Downloads]
        CDN3[Thumbnails]
    end
    
    APP[Application] --> C1
    APP --> C2
    APP --> Q1
    APP --> CDN1
```

### Query Optimization

**Optimized Query Example:**

```python
# ❌ Bad (N+1 queries)
files = DownloadableFile.objects.filter(is_active=True)
for file in files:
    print(file.uploaded_by.username)  # Extra query each time!

# ✅ Good (1 query)
files = DownloadableFile.objects.filter(
    is_active=True
).select_related('uploaded_by')  # Join in single query
for file in files:
    print(file.uploaded_by.username)  # No extra query!
```

---

## 📊 Database Schema

### DownloadableFile Table

```sql
CREATE TABLE downloads_downloadablefile (
    id BIGSERIAL PRIMARY KEY,
    category VARCHAR(4) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(4) NOT NULL,
    requires_login BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    tags VARCHAR(500),
    thumbnail VARCHAR(100),
    download_count INTEGER NOT NULL DEFAULT 0,
    view_count INTEGER NOT NULL DEFAULT 0,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    file_hash VARCHAR(64),
    uploaded_by_id BIGINT REFERENCES auth_user(id),
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER NOT NULL DEFAULT 0,
    file_type VARCHAR(10)
);

-- Indexes
CREATE INDEX downloads_d_categor_0ca7e6_idx 
    ON downloads_downloadablefile (category, is_active);

CREATE INDEX downloads_d_priorit_4e95c0_idx 
    ON downloads_downloadablefile (priority, is_featured);

CREATE INDEX downloads_d_uploade_f68532_idx 
    ON downloads_downloadablefile (uploaded_at);
```

---

## 🔌 Integration Points

### External Services

```mermaid
graph LR
    APP[Downloads App] --> CLAMAV[ClamAV Daemon]
    APP --> REDIS[Redis Cache]
    APP --> PG[PostgreSQL]
    APP --> CDN[CDN/CloudFront]
    APP --> STORAGE[File Storage]
    APP --> EMAIL[Email Service]
    
    CLAMAV -.->|Virus Scan Results| APP
    REDIS -.->|Cached Data| APP
    PG -.->|Query Results| APP
    CDN -.->|File URLs| APP
    STORAGE -.->|Files| APP
```

### Internal Dependencies

```mermaid
graph TB
    subgraph "Downloads App"
        D[Downloads]
    end
    
    subgraph "Core Django"
        AUTH[django.contrib.auth]
        ADMIN[django.contrib.admin]
        CACHE[django.core.cache]
    end
    
    subgraph "Third Party"
        DRF[djangorestframework]
        CELERY[Celery]
    end
    
    D --> AUTH
    D --> ADMIN
    D --> CACHE
    D -.->|Future| DRF
    D -.->|Future| CELERY
```

---

## 🚀 Deployment Architecture

### Production Setup

```mermaid
graph TB
    LB[Load Balancer] --> APP1[App Server 1]
    LB --> APP2[App Server 2]
    LB --> APP3[App Server 3]
    
    APP1 --> DB[(PostgreSQL Primary)]
    APP2 --> DB
    APP3 --> DB
    
    DB -.->|Replication| DR[(PostgreSQL Standby)]
    
    APP1 --> REDIS[(Redis Cluster)]
    APP2 --> REDIS
    APP3 --> REDIS
    
    APP1 --> STORAGE[S3/Object Storage]
    APP2 --> STORAGE
    APP3 --> STORAGE
    
    CDN[CloudFront CDN] --> STORAGE
    
    USERS[Users] --> CDN
    USERS --> LB
```

---

## 📈 Scalability Considerations

### Current Capacity
- **Files:** Up to 10,000 files
- **Concurrent Downloads:** ~100 req/sec
- **Storage:** Unlimited (cloud storage)

### Scalability Strategies
1. **Horizontal Scaling:** Add more app servers
2. **Caching:** Redis cluster for high availability
3. **CDN:** Offload file delivery
4. **Database:** Read replicas for queries
5. **Background Jobs:** Celery for async tasks

---

## 🔄 Future Enhancements

### Planned Architecture Changes

```mermaid
graph TB
    subgraph "Phase 1: Current"
        V1[Views] --> S1[Services]
        S1 --> M1[Models]
    end
    
    subgraph "Phase 2: API (Priority 3)"
        API[REST API] --> S2[Services]
        S2 --> M2[Models]
    end
    
    subgraph "Phase 3: Async (Priority 6)"
        TASKS[Celery Tasks] --> S3[Services]
        S3 --> M3[Models]
    end
    
    V1 -.->|Refactor| API
    S1 -.->|Enhance| TASKS
```

---

## 📚 References

- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

**Maintained By:** Bhanjyang Dev Team  
**Last Review:** January 6, 2026  
**Next Review:** March 2026
