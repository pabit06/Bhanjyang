# Home App (गृहपृष्ठ एप्लिकेसन)

The **Home App** is the central aggregator application for the Bhanjyang Cooperative project. It orchestrates content from various other applications (News, Services, About, Gallery) to create a cohesive landing page experience.

## 🏗 Architecture (संरचना)

The app follows a Service Layer pattern where `HomeService` acts as an aggregation facade. It does **not** duplicate logic but instead fetches and formats data from other domain services/models.

### Service Aggregation
`HomeService.get_home_context()` consolidates the following:
1.  **Page Content**: Managed locally (`HomePageContent`) for sliders/hero sections.
2.  **Testimonials**: Managed locally (`Testimonial`).
3.  **Statistics**: Fetched from `apps.about.models.CooperativeStatistic`.
4.  **Announcements**: Fetched from local `Announcement` and `apps.news_events.models.Notice`.
5.  **Services**: Fetched from `apps.services.models` (Savings, Loans, Fixed Deposits).
6.  **Gallery**: Fetched from `apps.gallery.models.GalleryImage`.

This design ensures the homepage always reflects the latest state of the entire system without tight coupling in views.

## ⚙️ Key Components

### Models
-   **HomePageContent**: Hero section sliders, introduction text.
-   **Testimonial**: Member testimonials with ratings.
-   **Statistic**: Fallback statistics (if About app unavailable).
-   **Announcement**: Urgent updates or banners.
-   **NewsletterSubscriber**: Simple subscription management.
-   **ContentVariant**: A/B testing infrastructure.

### Services (`services.py`)
-   **Caching**: Homepage data is cached for **5 minutes** (`CACHE_TIMEOUT_HOMEPAGE`) for non-staff users.
-   **Resilience**: All external app integrations are wrapped in `try-except` blocks. If `apps.services` crashes, the homepage still loads (just without featured services).
-   **Optimization**: Uses `select_related` and `prefetch_related` extensively.

## 🚀 Features

-   **Performance Optimized**: Aggressive caching and optimized queries.
-   **Fault Tolerant**: Partial system failures do not bring down the homepage.
-   **A/B Testing Ready**: Built-in support for content variants tracking.
-   **Search Engine Optimized (SEO)**: Meta tags support via `HomePageContent`.
-   **Bilingual**: Full Nepali language support.

## 🔧 Configuration (`constants.py`)

Configuration is centralized in `constants.py`:
```python
CACHE_TIMEOUT_HOMEPAGE = 300
LIMIT_TESTIMONIALS = 3
LIMIT_STATISTICS = 4
```

## 🧪 Testing

Comprehensive tests cover the aggregation logic:
-   `test_services.py`: Verifies data fetching and fallback mechanisms.
-   `test_views.py`: Verifies cache headers and response codes.
-   `test_models.py`: Verifies model constraints and methods.
-   `test_general.py`: Integration tests.

## 📝 Usage

### Adding a New Section
To add a new section (e.g., "Partners"):
1.  Add `_get_partners()` method in `HomeService`.
2.  Call it in `get_home_context()`.
3.  Add `partners` to the context dictionary.
4.  Update template `home/index.html`.

### Monitoring
Check `HomeService.get_error_context()` logs in Sentry/CloudWatch for backend failures.
