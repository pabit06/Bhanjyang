# About App - Complete Documentation (सम्पूर्ण दस्तावेज)

## 📋 Table of Contents (सामग्री सूची)

1. [Overview (अवलोकन)](#overview)
2. [Models (मोडेलहरू)](#models)
3. [Views (भ्यूहरू)](#views)
4. [Services (सेवाहरू)](#services)
5. [API Endpoints (API इन्डपोइन्टहरू)](#api-endpoints)
6. [Forms (फर्महरू)](#forms)
7. [Admin Interface (एडमिन इन्टरफेस)](#admin-interface)
8. [Analytics System (विश्लेषण प्रणाली)](#analytics-system)
9. [Caching System (क्यासिङ प्रणाली)](#caching-system)
10. [Templates (टेम्प्लेटहरू)](#templates)
11. [Management Commands (प्रबन्धन आदेशहरू)](#management-commands)
12. [Tests (परीक्षणहरू)](#tests)
13. [URL Patterns (URL प्याटर्नहरू)](#url-patterns)

---

## Overview (अवलोकन)

The **About App** is a comprehensive Django application that manages all "About Us" related content for the Bhanjyang Cooperative website. It handles cooperative information, timeline events, statistics, affiliations, leadership messages, team management, and user interactions.

**About App** भनेको Bhanjyang Cooperative वेबसाइटको "About Us" सम्बन्धी सबै सामग्री व्यवस्थापन गर्ने सम्पूर्ण Django application हो। यसले सहकारी जानकारी, टाइमलाइन घटनाहरू, तथ्याङ्क, सम्बन्ध, नेतृत्व सन्देशहरू, टोली व्यवस्थापन, र प्रयोगकर्ता अन्तरक्रियाहरू व्यवस्थापन गर्छ।

### Key Features (मुख्य विशेषताहरू)

- ✅ Cooperative Information Management (सहकारी जानकारी व्यवस्थापन)
- ✅ Timeline Events (टाइमलाइन घटनाहरू)
- ✅ Statistics Display (तथ्याङ्क प्रदर्शन)
- ✅ Affiliations & Partnerships (सम्बन्ध र साझेदारीहरू)
- ✅ Leadership Messages (नेतृत्व सन्देशहरू)
- ✅ Team & Committee Management (टोली र समिति व्यवस्थापन)
- ✅ Staff Management (कर्मचारी व्यवस्थापन)
# Newsletter Signup and Feedback System removed - no longer needed
- ✅ REST API (REST API)
- ✅ View-Level Caching (भ्यू-स्तर क्यासिङ)
- ✅ Service-Level Caching (सेवा-स्तर क्यासिङ)
- ✅ Multi-language Support (बहु-भाषा समर्थन)

---

## Models (मोडेलहरू)

### 1. CooperativeInfo (सहकारी जानकारी)

**Purpose:** Stores main cooperative information and details.

**Fields:**
- `cooperative_name` - Cooperative name (English)
- `cooperative_name_nepali` - Cooperative name (Nepali)
- `slug` - URL-friendly identifier (auto-generated)
- `established_date` - Date when cooperative was established
- `registration_number` - Registration number
- `license_number` - License number
- `address` - Physical address
- `phone` - Contact phone number
- `email` - Contact email
- `website` - Website URL (optional)
- `mission` - Mission statement
- `vision` - Vision statement
- `values` - Core values
- `description` - Detailed description (English)
- `description_nepali` - Detailed description (Nepali)
- `logo` - Cooperative logo image
- `featured_image` - Featured image
- `is_active` - Active status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Custom Manager:** `ContentManager` with `active()` and `featured()` methods

**Indexes:**
- `slug` - For URL lookups
- `is_active` - For filtering active items
- `created_at`, `updated_at` - For date-based queries
- `cooperative_name` - For search

**Methods:**
- `get_absolute_url()` - Returns URL for detail view

---

### 2. CooperativeTimeline (सहकारी टाइमलाइन)

**Purpose:** Stores timeline events and milestones.

**Fields:**
- `title` - Event title
- `description` - Event description
- `event_date` - Date of the event
- `event_type` - Type of event (milestone, achievement, expansion, award, partnership, other)
- `image` - Event image (optional)
- `order` - Display order
- `is_featured` - Featured status
- `is_active` - Active status
- `created_at`, `updated_at` - Timestamps

**Event Types:**
- `milestone` - Important milestones
- `achievement` - Achievements
- `expansion` - Expansion events
- `award` - Awards received
- `partnership` - Partnerships
- `other` - Other events

**Indexes:**
- `is_active`, `is_featured`, `event_date` - Composite index
- `event_type`, `is_active` - For filtering by type
- `event_date` - For date-based queries
- `title` - For search

---

### 3. CooperativeStatistic (सहकारी तथ्याङ्क)

**Purpose:** Stores cooperative statistics and metrics.

**Fields:**
- `title` - Statistic title
- `value` - Statistic value
- `unit` - Unit of measurement (optional)
- `description` - Description (optional)
- `statistic_type` - Type of statistic
- `icon` - Icon class name (optional)
- `color` - Color theme (default: 'deuraligreen')
- `order` - Display order
- `is_featured` - Featured status
- `is_active` - Active status
- `created_at`, `updated_at` - Timestamps

**Statistic Types:**
- `members` - Total Members
- `deposits` - Total Deposits
- `loans` - Total Loans Disbursed
- `branches` - Number of Branches
- `employees` - Number of Employees
- `assets` - Total Assets
- `other` - Other statistics

**Indexes:**
- `is_active`, `is_featured` - For filtering
- `statistic_type`, `is_active` - For filtering by type
- `order` - For ordering
- `title` - For search

---

### 4. CooperativeAffiliation (सहकारी सम्बन्ध)

**Purpose:** Stores cooperative affiliations and partnerships.

**Fields:**
- `name` - Organization name
- `description` - Description
- `affiliation_type` - Type of affiliation
- `website` - Organization website (optional)
- `logo` - Organization logo (optional)
- `order` - Display order
- `is_featured` - Featured status
- `is_active` - Active status
- `created_at`, `updated_at` - Timestamps

**Affiliation Types:**
- `regulatory` - Regulatory Body
- `association` - Professional Association
- `partnership` - Partnership
- `certification` - Certification Body
- `other` - Other

**Indexes:**
- `is_active`, `is_featured` - For filtering
- `affiliation_type`, `is_active` - For filtering by type
- `order` - For ordering
- `name` - For search

---

### 5. LeadershipMessage (नेतृत्व सन्देश)

**Purpose:** Stores leadership messages from key personnel.

**Fields:**
- `title` - Message title
- `message_type` - Type of message
- `content` - Message content
- `author_name` - Author's name
- `author_position` - Author's position
- `author_photo` - Author's photo (optional)
- `order` - Display order
- `is_featured` - Featured status
- `is_active` - Active status
- `created_at`, `updated_at` - Timestamps

**Message Types:**
- `chairman` - Chairman Message
- `manager` - Manager Message
- `director` - Director Message
- `other` - Other

**Indexes:**
- `is_active`, `is_featured` - For filtering
- `message_type`, `is_active` - For filtering by type
- `order` - For ordering
- `title`, `author_name` - For search

---

### 6. Person (व्यक्ति)

**Purpose:** Represents a unique person in the cooperative (used for team management).

**Fields:**
- `full_name` - Full name (unique)
- `photo` - Person's photo (optional)
- `bio` - Brief biography (optional)
- `email` - Email address (optional)
- `phone` - Phone number (optional)
- `position_general` - General position (optional)
- `is_active` - Active status
- `created_at`, `updated_at` - Timestamps

**Indexes:**
- `full_name` - For search
- `is_active` - For filtering
- `email` - For email lookups

**Relationships:**
- One-to-many with `Membership` (via `memberships`)
- One-to-one with `Staff` (via `staff_profile`)

---

### 7. Committee (समिति)

**Purpose:** Represents a specific committee for a specific tenure.

**Fields:**
- `name` - Committee name (e.g., सञ्चालक समिति, लेखा समिति)
- `tenure_bs` - Tenure in Bikram Sambat (e.g., २०८०-२०८३)
- `slug` - URL-friendly identifier (auto-generated)
- `is_active` - Active status (current committees)
- `order` - Display order
- `description` - Committee description (optional)
- `start_date` - Start date (optional)
- `end_date` - End date (optional)

**Indexes:**
- `slug` - For URL lookups
- `is_active`, `order` - For filtering and ordering
- `name` - For search
- `tenure_bs` - For filtering by tenure

**Relationships:**
- One-to-many with `Membership` (via `memberships`)

**Methods:**
- `save()` - Auto-generates slug from name and tenure

---

### 8. Membership (सदस्यता)

**Purpose:** Links a Person to a Committee with a position.

**Fields:**
- `person` - ForeignKey to Person
- `committee` - ForeignKey to Committee
- `position` - Position in committee (e.g., अध्यक्ष, सदस्य, ऋण संयोजक)
- `order` - Order within committee
- `start_date` - Start date (optional)
- `end_date` - End date (optional)
- `is_active` - Active status

**Constraints:**
- `unique_together` - (`person`, `committee`) - One person can only have one membership per committee

**Indexes:**
- `committee`, `order` - For committee-based queries
- `person`, `committee` - For unique lookup optimization
- `is_active` - For filtering
- `position` - For filtering by position

---

### 9. Staff (कर्मचारी)

**Purpose:** Represents a Staff Member.

**Fields:**
- `person` - OneToOneField to Person
- `position` - Staff position (e.g., Manager, Accountant)
- `start_date` - Date staff member joined (optional)
- `is_active` - Currently employed status
- `order` - Display order
- `department` - Department (optional)
- `salary_range` - Salary range (optional)
- `qualifications` - Qualifications (optional)

**Indexes:**
- `person` - For person lookups
- `is_active`, `order` - For filtering and ordering
- `position` - For filtering by position
- `department` - For filtering by department

---

---

## Views (भ्यूहरू)

### Class-Based Views (क्लास-आधारित भ्यूहरू)

#### 1. AboutHomeView
- **Type:** RedirectView
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Redirects `/about/` to `/about/introduction/`
- **Redirect:** `about:introduction`

#### 2. IntroductionView
- **Template:** `about/introduction.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Main introduction page with Our Story, Vision & Mission, and Timeline
- **Context Data:**
  - `cooperative_info` - Active cooperative information
  - `timeline_events` - Featured timeline events (max 6)
  - `breadcrumbs` - Navigation breadcrumbs

#### 3. TimelineView
- **Template:** `about/timeline.html`
- **Caching:** 600 seconds (10 minutes)
- **Pagination:** 12 items per page
- **Purpose:** Display all timeline events
- **Context:** `page_obj` (paginated timeline events), `breadcrumbs`

#### 4. AffiliationsView
- **Template:** `about/affiliations.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Display all affiliations
- **Context:** `affiliations`, `breadcrumbs`

#### 5. ChairpersonMessageView
- **Template:** `about/chairperson_message.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Display chairperson message
- **Context:** `message`, `breadcrumbs`

#### 6. ManagerCommitmentView
- **Template:** `about/manager_commitment.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Display manager commitment message
- **Context:** `message`, `breadcrumbs`

#### 7. BoardOfDirectorsView
- **Template:** `about/board_of_directors.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Display board of directors (committees)
- **Context:** `committees`, `breadcrumbs`

#### 8. ManagementView
- **Template:** `about/management.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Display management team (staff)
- **Context:** `management_team`, `breadcrumbs`

#### 9. MemberTestimonialsView
- **Template:** `about/member_testimonials.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Display member testimonials
- **Context:** `testimonials`, `breadcrumbs`

#### 10. CooperativeDetailView
- **Template:** `about/cooperative_detail.html`
- **Caching:** 600 seconds (10 minutes)
- **Purpose:** Display detailed cooperative information
- **Lookup:** By slug
- **Context:** `cooperative`, `breadcrumbs`

**Note:** GalleryView has been removed. Use the main gallery app at `/gallery/` instead.

### Function-Based Views (फंक्शन-आधारित भ्यूहरू)

#### 8. ContactView
- **Type:** RedirectView
- **Purpose:** Redirects to main contact app (`contact:contact_view`)
- **Note:** Contact form functionality has been consolidated to the contact app for unified database storage

# NewsletterSignupView and FeedbackView removed - no longer needed

---

## Services (सेवाहरू)

### AboutService Class

Service layer for business logic and data fetching.

#### Methods:

1. **`get_about_home_data(is_staff=False)`**
   - Retrieves all data for main About Us page
   - Caches results for 10 minutes (non-staff users)
   - Returns: cooperative_info, timeline_events, statistics, affiliations, leadership_messages, counts, breadcrumbs

2. **`get_timeline_events()`**
   - Returns all active timeline events ordered by date (newest first)

3. **`get_affiliations()`**
   - Returns all active affiliations ordered by display order

4. **`get_leadership_messages()`**
   - Returns all active leadership messages ordered by display order

5. **`get_active_team()`**
   - Returns tuple of (committees, staff)
   - Uses prefetch_related and select_related for optimization
   - Returns active committees with memberships and active staff

6. **`get_past_committees()`**
   - Returns inactive (past) committees ordered by tenure
   - Uses prefetch_related for optimization

7. **`send_contact_emails(data)`**
   - **DEPRECATED:** Sends contact form notification emails
   - **Note:** This method is kept for backward compatibility with tests only
   - New contact submissions should use `ContactService` from contact app
   - Respects SEND_REAL_EMAILS setting
   - Returns: True/False

# send_newsletter_welcome_email and send_feedback_email methods removed - no longer needed

---

## API Endpoints (API इन्डपोइन्टहरू)

### REST API Viewsets

All viewsets support:
- Pagination (20 items per page, max 100)
- Filtering (DjangoFilterBackend)
- Searching (SearchFilter)
- Ordering (OrderingFilter)

#### 1. CooperativeInfoViewSet
- **Base URL:** `/api/v1/about/cooperative-info/`
- **Actions:**
  - `GET /` - List all active cooperative info
  - `GET /{id}/` - Retrieve specific cooperative info
  - `GET /featured/` - Get featured cooperative info
  - `GET /statistics/` - Get cooperative statistics
- **Search Fields:** cooperative_name, description, mission, vision, values
- **Ordering:** created_at, updated_at

#### 2. CooperativeTimelineViewSet
- **Base URL:** `/api/v1/about/timeline/`
- **Actions:**
  - `GET /` - List all active timeline events
  - `GET /{id}/` - Retrieve specific timeline event
  - `GET /featured/` - Get featured timeline events (max 5)
  - `GET /recent/` - Get recent timeline events (max 10)
- **Filters:** event_type, is_featured
- **Search Fields:** title, description
- **Ordering:** event_date, created_at, order

#### 3. CooperativeAffiliationViewSet
- **Base URL:** `/api/v1/about/affiliations/`
- **Actions:**
  - `GET /` - List all active affiliations
  - `GET /{id}/` - Retrieve specific affiliation
  - `GET /featured/` - Get featured affiliations (max 5)
- **Search Fields:** name, description
- **Ordering:** created_at, order

#### 4. LeadershipMessageViewSet
- **Base URL:** `/api/v1/about/leadership/`
- **Actions:**
  - `GET /` - List all active leadership messages
  - `GET /{id}/` - Retrieve specific leadership message
  - `GET /featured/` - Get featured leadership messages (max 3)
- **Search Fields:** title, content, author_name, author_position
- **Ordering:** created_at, order

#### 5. PersonViewSet
- **Base URL:** `/api/v1/about/team/`
- **Actions:**
  - `GET /` - List all active team members
  - `GET /{id}/` - Retrieve specific team member
  - `GET /current_team/` - Get current team members
  - `GET /past_team/` - Get past team members
  - `GET /by_position/?position={position}` - Get team members by position
- **Search Fields:** full_name, bio, position_general
- **Ordering:** created_at, full_name

#### 6. CommitteeViewSet
- **Base URL:** `/api/v1/about/committees/`
- **Actions:**
  - `GET /` - List all active committees
  - `GET /{id}/` - Retrieve specific committee
  - `GET /{id}/members/` - Get committee members
- **Search Fields:** name, description
- **Ordering:** created_at, order

#### 7. StaffViewSet
- **Base URL:** `/api/v1/about/staff/`
- **Actions:**
  - `GET /` - List all active staff members
  - `GET /{id}/` - Retrieve specific staff member
  - `GET /by_department/?department={department}` - Get staff by department
- **Search Fields:** person__full_name, position, department
- **Ordering:** created_at, person__full_name

### Additional API Endpoints

#### 8. SearchAPIView
- **URL:** `/api/v1/about/search/?q={query}`
- **Method:** GET
- **Purpose:** Global search across all about app models
- **Returns:** Search results for cooperative_info, timeline, affiliations, leadership, team
- **Caching:** 5 minutes

#### 9. StatisticsAPIView
- **URL:** `/api/v1/about/statistics/`
- **Method:** GET
- **Purpose:** Get site statistics
- **Returns:** Counts for all models, last_updated timestamp
- **Caching:** 1 hour

#### 10. ContactAPIView
- **REMOVED:** ContactAPIView has been removed from about app.
- **Use:** Contact app's API endpoint instead
- **Reason:** Consolidation ensures all contact submissions are saved to the database

# NewsletterAPIView removed - no longer needed

---

## Forms (फर्महरू)

### 1. ContactForm
**REMOVED:** ContactForm has been removed from about app.
**Use:** Contact app's `ContactForm` instead (`apps/contact/forms.py`)
**Reason:** Consolidation ensures all contact submissions are saved to the database

---

# NewsletterSignupForm and FeedbackForm removed - no longer needed

---

## Admin Interface (एडमिन इन्टरफेस)

All models are registered with custom admin site (`apps.admin.admin_site`).

### Custom Filters

#### ActiveFilter
- Filters items by active/inactive status
- Used in: CooperativeInfo, CooperativeTimeline

#### FeaturedFilter
- Filters items by featured status
- Used in: CooperativeTimeline

### Admin Classes

#### 1. CooperativeInfoAdmin
- **List Display:** cooperative_name, established_date, registration_number, is_active, created_at, actions_column
- **Filters:** ActiveFilter, established_date, created_at
- **Search:** cooperative_name, cooperative_name_nepali, description, registration_number
- **Actions:** activate_selected, deactivate_selected
- **Fieldsets:** Basic Information, Cooperative Details, Contact Information, Mission & Vision, Description, Media, Status

#### 2. CooperativeTimelineAdmin
- **List Display:** title, event_date, event_type, is_featured, is_active, order
- **List Editable:** order, is_featured, is_active
- **Filters:** ActiveFilter, FeaturedFilter, event_type, event_date
- **Date Hierarchy:** event_date
- **Actions:** activate_selected, deactivate_selected, feature_selected, unfeature_selected

#### 3. CooperativeStatisticAdmin
- **List Display:** title, value, unit, statistic_type, is_featured
- **Filters:** statistic_type, is_featured, is_active
- **Fieldsets:** Basic, Visual Settings, Display Settings

#### 4. CooperativeAffiliationAdmin
- **List Display:** name, affiliation_type, is_featured, is_active
- **Filters:** affiliation_type, is_featured, is_active
- **Fieldsets:** Basic, Media, Display Settings

#### 5. LeadershipMessageAdmin
- **List Display:** title, author_name, author_position, message_type, is_featured
- **Filters:** message_type, is_featured, is_active
- **Fieldsets:** Basic, Author Information, Display Settings

#### 6. PersonAdmin
- **List Display:** full_name, email, phone, position_general, is_active, created_at
- **Filters:** is_active, created_at
- **Fieldsets:** Basic Information, Contact Information, Status, Timestamps

#### 7. CommitteeAdmin
- **List Display:** name, tenure_bs, is_active, order, member_count
- **Inlines:** MembershipInline (TabularInline)
- **Autocomplete:** person (in inline)
- **Fieldsets:** Basic Information, Dates, Display Settings

#### 8. MembershipAdmin
- **List Display:** person, committee, position, order, is_active
- **Filters:** is_active, committee
- **Autocomplete:** person, committee
- **Fieldsets:** Membership Information, Dates, Display Settings

#### 9. StaffAdmin
- **List Display:** person, position, department, is_active, order
- **Filters:** is_active, department
- **Autocomplete:** person
- **Fieldsets:** Staff Information, Employment Details, Display Settings

---

## Caching System (क्यासिङ प्रणाली)

The About app uses Django's built-in caching framework for optimal performance.

### View-Level Caching

Most views use `@cache_page(600)` decorator to cache responses for 10 minutes:
- `AboutHomeView` - Redirects to introduction page
- `IntroductionView` - Main introduction page
- `TimelineView` - Timeline events list
- `AffiliationsView` - Affiliations page
- `ChairpersonMessageView` - Chairperson message
- `ManagerCommitmentView` - Manager commitment
- `BoardOfDirectorsView` - Board of directors
- `ManagementView` - Management team
- `MemberTestimonialsView` - Member testimonials
- `CooperativeDetailView` - Cooperative detail page

### Service-Level Caching

The `AboutService` class implements caching for data fetching:
- `get_about_home_data()` - Caches home page data for 10 minutes (non-staff users)
- Uses Django's `cache` framework directly
- Cache keys are prefixed with model names for easy invalidation

### Cache Configuration

Caching is configured via Django settings:
- Uses `CACHE_TIMEOUT_MEDIUM` (600 seconds) from `constants.py`
- Respects `is_staff` flag to bypass cache for admin users
- Cache invalidation handled automatically on model updates

---

## Templates (टेम्प्लेटहरू)

All templates are located in `apps/about/templates/about/`:

1. **introduction.html** - Main About Us introduction page (redirected from `/about/`)
2. **timeline.html** - Timeline events page
3. **affiliations.html** - Affiliations page
4. **chairperson_message.html** - Chairperson message page
5. **manager_commitment.html** - Manager commitment page
6. **board_of_directors.html** - Board of directors page
7. **management.html** - Management team page
8. **member_testimonials.html** - Member testimonials page
9. **cooperative_detail.html** - Cooperative detail page

**Note:** 
- The `about.html` template has been removed - `/about/` now redirects to `/about/introduction/`
- Contact form templates have been removed - use main contact app at `/contact/` instead
- Gallery template has been removed - use main gallery app at `/gallery/` instead

All templates extend `base.html` and include breadcrumbs for navigation.

---

## Management Commands (प्रबन्धन आदेशहरू)

### populate_about.py

**Purpose:** Populate initial data for about app

**Usage:**
```bash
python manage.py populate_about
```

**Features:**
- Creates sample cooperative information
- Creates sample timeline events
- Creates sample statistics
- Creates sample affiliations
- Creates sample leadership messages
- Creates sample team data (committees, members, staff)

---

## Tests (परीक्षणहरू)

Test files located in `apps/about/tests/`:

1. **test_admin.py** - Admin interface tests
2. **test_analytics.py** - Analytics system tests
3. **test_api_views.py** - API endpoint tests
4. **test_cache_utils.py** - Caching system tests
5. **test_forms.py** - Form validation tests
6. **test_general.py** - General model and view tests
7. **test_management_commands.py** - Management command tests
8. **test_serializers.py** - Serializer tests
9. **test_services_comprehensive.py** - Comprehensive service tests
10. **test_templatetags.py** - Template tag tests

**Test Coverage:** >80% (maintained)

**Run Tests:**
```bash
# Run all about app tests
pytest apps/about/tests/

# Run specific test file
pytest apps/about/tests/test_views.py

# Run with coverage
pytest apps/about/tests/ --cov=apps.about
```

---

## URL Patterns (URL प्याटर्नहरू)

### Main URLs (`apps/about/urls.py`)

```python
app_name = 'about'

urlpatterns = [
    # Main about page - redirect to introduction
    path('', views.AboutHomeView.as_view(), name='home'),
    
    # Sub-pages
    path('introduction/', views.IntroductionView.as_view(), name='introduction'),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('affiliations/', views.AffiliationsView.as_view(), name='affiliations'),
    path('chairperson-message/', views.ChairpersonMessageView.as_view(), name='chairperson_message'),
    path('manager-commitment/', views.ManagerCommitmentView.as_view(), name='manager_commitment'),
    
    # Team pages
    path('board-of-directors/', views.BoardOfDirectorsView.as_view(), name='board_of_directors'),
    path('management/', views.ManagementView.as_view(), name='management'),
    
    # Testimonials
    path('member-testimonials/', views.MemberTestimonialsView.as_view(), name='member_testimonials'),
    
    # Form handling
    path('contact/', views.ContactView.as_view(), name='contact'),  # Redirects to main contact app
    # Newsletter and Feedback forms removed - no longer needed
    
    # Cooperative detail
    path('cooperative/<slug:slug>/', views.CooperativeDetailView.as_view(), name='cooperative_detail'),
]
```

### API URLs (`apps/about/api_urls.py`)

```python
app_name = 'about_api'

urlpatterns = [
    # API router URLs
    path('', include(router.urls)),
    
    # Additional API endpoints
    path('search/', SearchAPIView.as_view(), name='search'),
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),
    # Note: Contact API endpoint removed - use contact app's API instead
    # Newsletter API endpoint removed - no longer needed
]
```

**Registered Viewsets:**
- `cooperative-info/` - CooperativeInfoViewSet
- `timeline/` - CooperativeTimelineViewSet
- `affiliations/` - CooperativeAffiliationViewSet
- `leadership/` - LeadershipMessageViewSet
- `team/` - PersonViewSet
- `committees/` - CommitteeViewSet
- `staff/` - StaffViewSet

---

## Static Files (स्थिर फाइलहरू)

Located in `apps/about/static/about/`:

- **CSS files** - App-specific styles
- **JavaScript files** - Interactive features
- **Images** - App-specific images (if any)

---

## Templatetags (टेम्प्लेट ट्यागहरू)

Custom template tags located in `apps/about/templatetags/`:

- Custom filters and tags for template rendering
- Used in templates for data formatting and display

---

## Dependencies (निर्भरताहरू)

### External Packages:
- `django` - Django framework
- `djangorestframework` - REST API framework
- `django-filter` - Filtering for API
- `django-redis` - Redis cache backend (optional)

### Internal Dependencies:
- `apps.core` - Core utilities (error_handling, view_mixins, query_utils)
- `apps.admin` - Custom admin site

---

## Best Practices (उत्तम अभ्यासहरू)

1. **Service Layer Pattern** - All business logic in `AboutService`
2. **Caching** - View-level caching (10 minutes) and service-level caching for performance
3. **Database Indexes** - Comprehensive indexes for all models
4. **Query Optimization** - Use prefetch_related and select_related
5. **Error Handling** - Comprehensive error handling with `apps.core.error_handling` utilities
6. **Type Hints** - All service methods have type hints
7. **Docstrings** - Comprehensive documentation for all classes and methods
8. **Testing** - >80% test coverage maintained
9. **API Design** - RESTful API with pagination, filtering, searching
10. **View Optimization** - Optimized querysets with proper select_related/prefetch_related

---

## Future Enhancements (भविष्यका सुधारहरू)

- [ ] Advanced search with full-text search
- [ ] Image optimization for uploaded images
- [ ] Multi-language content management
- [ ] Webhook support for API
- [ ] GraphQL API endpoint
- [ ] Real-time notifications
- [ ] Advanced reporting features
- [ ] Export functionality for data

---

## Support & Maintenance (समर्थन र मर्मत)

For issues, questions, or contributions:
- Check test files for usage examples
- Review service methods for business logic
- Check admin interface for data management
- Review API documentation for integration

---

**Last Updated:** 2025
**Version:** 1.0
**Maintained By:** Bhanjyang Cooperative Development Team

