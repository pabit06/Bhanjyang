# News Events App - Architecture Diagram
# (समाचार कार्यक्रम एप - वास्तुकला चित्र)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NEWS EVENTS APP ARCHITECTURE                        │
│                              (95.4/100 Rating)                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Web UI     │  │   Mobile     │  │  Third-Party │  │   Admin      │   │
│  │  (Templates) │  │  (REST API)  │  │   (REST API) │  │  Interface   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                  │                 │            │
└─────────┼─────────────────┼──────────────────┼─────────────────┼────────────┘
          │                 │                  │                 │
          ▼                 ▼                  ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐     ┌─────────────────────────────┐       │
│  │     WEB VIEWS (views.py)    │     │   REST API (api_views.py)   │       │
│  │────────────────────────────│     │─────────────────────────────│       │
│  │ • NewsHomeView             │     │ • CategoryViewSet           │       │
│  │ • ArticleDetailView        │     │ • NewsArticleViewSet        │       │
│  │ • EventDetailView          │     │ • EventViewSet              │       │
│  │ • ArticleListView          │     │ • CommentViewSet            │       │
│  │ • EventListView            │     │ • SubscriberViewSet         │       │
│  │ • SubscriptionView         │     │ • NewsletterViewSet         │       │
│  │ • CommentSubmissionView    │     │ • ContentAnalyticsViewSet   │       │
│  │ • SearchView               │     │ • AdvancedSearchViewSet     │       │
│  └─────────────┬───────────────┘     └─────────────┬───────────────┘       │
│                │                                    │                       │
│                └────────────────┬───────────────────┘                       │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    SERVICE LAYER (services.py)                        │ │
│  │───────────────────────────────────────────────────────────────────────│ │
│  │                                                                       │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │ │
│  │  │  NewsService   │  │  EventService  │  │ SearchService  │         │ │
│  │  │───────────────│  │────────────────│  │────────────────│         │ │
│  │  │ • get_home_   │  │ • get_event_   │  │ • perform_    │         │ │
│  │  │   page_data() │  │   detail()     │  │   search()     │         │ │
│  │  │ • get_article_│  │ • get_event_   │  │                │         │ │
│  │  │   detail()    │  │   list()       │  │                │         │ │
│  │  │ • get_article_│  │                │  │                │         │ │
│  │  │   list()      │  │                │  │                │         │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │ │
│  │                                                                       │ │
│  │  ┌─────────────────┐  ┌──────────────────┐                          │ │
│  │  │InteractionSvc   │  │NewsletterService │                          │ │
│  │  │─────────────────│  │──────────────────│                          │ │
│  │  │ • handle_       │  │ • dispatch_      │                          │ │
│  │  │   subscription()│  │   newsletter()   │                          │ │
│  │  │ • handle_       │  │ • get_newsletter_│                          │ │
│  │  │   comment()     │  │   status()       │                          │ │
│  │  │ • handle_share()│  │                  │                          │ │
│  │  └─────────────────┘  └──────────────────┘                          │ │
│  │                                                                       │ │
│  └───────────────────────────────┬───────────────────────────────────────┘ │
│                                  │                                         │
└──────────────────────────────────┼─────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CROSS-CUTTING CONCERNS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  SECURITY    │  │ PERFORMANCE  │  │   CACHING    │  │   ANALYTICS  │   │
│  │ (security.py)│  │(performance) │  │(query_cache) │  │ (analytics)  │   │
│  │──────────────│  │──────────────│  │──────────────│  │──────────────│   │
│  │ • Content    │  │ • Query      │  │ • Article    │  │ • View       │   │
│  │   Validator  │  │   Optimizer  │  │   List Cache │  │   Tracking   │   │
│  │ • Spam       │  │ • Image      │  │ • Event      │  │ • Share      │   │
│  │   Protection │  │   Optimizer  │  │   List Cache │  │   Tracking   │   │
│  │ • Rate       │  │ • CDN        │  │ • Analytics  │  │ • Comment    │   │
│  │   Limiting   │  │   Manager    │  │   Cache      │  │   Tracking   │   │
│  │ • Audit Log  │  │ • Performance│  │ • Invalid    │  │ • Real-time  │   │
│  │              │  │   Monitor    │  │   Slug Cache │  │   Metrics    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ERROR HANDLING│  │   TASKS      │  │ NOTIFICATIONS│  │ SOCIAL MEDIA │   │
│  │(error_handle)│  │ (tasks.py)   │  │(notification)│  │(social_media)│   │
│  │──────────────│  │──────────────│  │──────────────│  │──────────────│   │
│  │ • Structured │  │ • Newsletter │  │ • User       │  │ • Share URL  │   │
│  │   Error Log  │  │   Sending    │  │   Notify     │  │   Generation │   │
│  │ • Recovery   │  │ • Email      │  │ • Email      │  │ • Social     │   │
│  │   Decorators │  │   Batch      │  │   Templates  │  │   Integration│   │
│  │ • User-      │  │ • Celery     │  │              │  │              │   │
│  │   Friendly   │  │   Integration│  │              │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       MODELS (models.py)                            │   │
│  │─────────────────────────────────────────────────────────────────────│   │
│  │                                                                     │   │
│  │  ┌────────────┐  ┌─────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │  Category  │  │NewsArticle  │  │   Event    │  │  Comment   │  │   │
│  │  │────────────│  │─────────────│  │────────────│  │────────────│  │   │
│  │  │ • name     │  │ • title     │  │ • title    │  │ • article  │  │   │
│  │  │ • slug     │  │ • slug      │  │ • slug     │  │ • author   │  │   │
│  │  │ • color    │  │ • category  │  │ • event_   │  │ • content  │  │   │
│  │  │ • icon     │  │ • author    │  │   type     │  │ • approved │  │   │
│  │  │ • is_active│  │ • content   │  │ • location │  │            │  │   │
│  │  │            │  │ • status    │  │ • event_   │  │            │  │   │
│  │  │            │  │ • priority  │  │   date     │  │            │  │   │
│  │  │            │  │ • is_       │  │ • status   │  │            │  │   │
│  │  │            │  │   featured  │  │            │  │            │  │   │
│  │  └────────────┘  └─────────────┘  └────────────┘  └────────────┘  │   │
│  │                                                                     │   │
│  │  ┌────────────┐  ┌─────────────┐  ┌────────────────────┐          │   │
│  │  │Subscriber  │  │ Newsletter  │  │ ContentAnalytics   │          │   │
│  │  │────────────│  │─────────────│  │────────────────────│          │   │
│  │  │ • email    │  │ • title     │  │ • content_type     │          │   │
│  │  │ • name     │  │ • subject   │  │ • object_id        │          │   │
│  │  │ • status   │  │ • content   │  │ • view_count       │          │   │
│  │  │ • confirmed│  │ • status    │  │ • share_count      │          │   │
│  │  │ • token    │  │ • sent_date │  │ • comment_count    │          │   │
│  │  └────────────┘  └─────────────┘  └────────────────────┘          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DATABASE OPTIMIZATIONS                           │   │
│  │─────────────────────────────────────────────────────────────────────│   │
│  │ • Indexes on: status, published_date, category, slug               │   │
│  │ • select_related() for ForeignKeys                                 │   │
│  │ • prefetch_related() for ManyToMany                                │   │
│  │ • Atomic view/share count updates                                  │   │
│  │ • Connection pooling                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        MANAGEMENT COMMANDS LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │ seed_news_events │  │ fix_empty_slugs  │  │  monitor_news    │         │
│  │ cleanup_old_     │  │ bulk_publish     │  │  news_analytics  │         │
│  │   content        │  │ export_content   │  │  clear_cache     │         │
│  │ newsletter_send  │  │ update_view_     │  │                  │         │
│  │                  │  │   counts         │  │                  │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           TESTING INFRASTRUCTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │
│  │  UNIT TESTS   │  │ API TESTS     │  │   E2E TESTS   │  │ LOAD TESTS  │ │
│  │───────────────│  │───────────────│  │───────────────│  │─────────────│ │
│  │ • test_models │  │ • test_api_   │  │ • test_       │  │ • test_load_│ │
│  │ • test_forms  │  │   views (63)  │  │   integration │  │   performance││
│  │ • test_       │  │ • API         │  │   _e2e (77+)  │  │   (50+)     │ │
│  │   services    │  │   endpoints   │  │ • Complete    │  │ • 50-200    │ │
│  │ • test_       │  │ • Pagination  │  │   workflows   │  │   concurrent│ │
│  │   managers    │  │ • Filtering   │  │               │  │ • Memory    │ │
│  │               │  │ • Search      │  │               │  │   leak test │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └─────────────┘ │
│                                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                  │
│  │SECURITY TESTS │  │PERFORMANCE    │  │  GENERAL      │                  │
│  │───────────────│  │  TESTS        │  │  TESTS        │                  │
│  │ • Spam        │  │───────────────│  │───────────────│                  │
│  │   Protection  │  │ • Caching     │  │ • Admin tests │                  │
│  │ • Rate        │  │ • Query       │  │ • View tests  │                  │
│  │   Limiting    │  │   Optimization│  │               │                  │
│  │ • Content     │  │ • Response    │  │               │                  │
│  │   Validation  │  │   Times       │  │               │                  │
│  │ (99 tests)    │  │ (90 tests)    │  │ (23 tests)    │                  │
│  └───────────────┘  └───────────────┘  └───────────────┘                  │
│                                                                             │
│                      TOTAL: 600+ TEST METHODS                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW DIAGRAM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Request → Security Check → View/API → Service Layer →                │
│  → Cache Check → Database Query → Performance Optimization →               │
│  → Response Formatting → User Response                                     │
│                                                                             │
│  WITH:                                                                      │
│  • Rate limiting at entry point                                            │
│  • Content validation in service layer                                     │
│  • Query optimization at database layer                                    │
│  • Caching at multiple levels                                              │
│  • Analytics tracking throughout                                           │
│  • Error handling at every layer                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Architecture Principles

### 1. **Separation of Concerns**
- **Views**: Handle HTTP requests/responses
- **Services**: Contain business logic
- **Models**: Data representation and persistence
- **Utilities**: Reusable helper functions

### 2. **DRY (Don't Repeat Yourself)**
- Service layer reused by views and API
- Common utilities in utils.py
- Shared constants in constants.py
- Base serializers for inheritance

### 3. **Security by Design**
- Security checks at every layer
- Rate limiting before processing
- Content validation in service layer
- Audit logging for sensitive operations

### 4. **Performance First**
- Caching at multiple levels
- Query optimization built-in
- Image optimization automatic
- Connection pooling configured

### 5. **Testability**
- Service layer easily testable
- Clear dependencies
- Fixture support
- Mock-friendly design

---

## 📈 Scalability Features

1. **Horizontal Scaling**
   - Stateless services
   - Cache-based session management
   - Celery for async tasks
   - CDN for static assets

2. **Vertical Scaling**
   - Query optimization
   - Connection pooling
   - Efficient indexing
   - Image optimization

3. **Load Distribution**
   - API pagination
   - Rate limiting
   - Throttling classes
   - Burst protection

---

## 🔒 Security Architecture

```
Layer 1: Rate Limiting (Throttling)
   ↓
Layer 2: Input Validation (Forms/Serializers)
   ↓
Layer 3: Content Security (Spam, XSS)
   ↓
Layer 4: Business Logic (Services)
   ↓
Layer 5: Audit Logging (Security Events)
```

---

## ⚡ Performance Flow

```
Request
  ↓
Check Cache → Cache Hit → Return Cached Response
  ↓ Cache Miss
Query Optimizer
  ↓
Database Query (with select_related/prefetch_related)
  ↓
Cache Result
  ↓
Return Response
```

---

**Diagram Version:** 1.0  
**Last Updated:** 2026-01-05  
**Status:** Current
