# Test Coverage Improvement Plan

## Current Status
- ✅ **All 212 tests passing**
- ⚠️ **Coverage: 58%** (Target: 80%)
- **Gap: 22%** (~2,800 lines need testing)

## Priority Areas for Testing

### 1. Services Layer (High Priority)
**Current Coverage: 0-33%**

#### `apps/about/services.py` (33% coverage)
- [ ] Test `send_contact_emails()` with different email settings
- [ ] Test `send_newsletter_welcome_email()`
- [ ] Test `send_feedback_email()`
- [ ] Test error handling paths

#### `apps/contact/services.py` (0% coverage)
- [ ] Test `ContactService.handle_submission()`
- [ ] Test `KYMService.process_kym_submission()`
- [ ] Test `ContactAnalyticsService` methods
- [ ] Test email sending logic

#### `apps/downloads/services.py` (0% coverage)
- [ ] Test `DownloadsService` methods
- [ ] Test `FileDownloadService` methods
- [ ] Test `BulkDownloadService` methods
- [ ] Test `DownloadsAnalyticsService` methods

#### `apps/home/services.py` (27% coverage)
- [ ] Test `get_home_context()` with various scenarios
- [ ] Test `handle_contact_submission()`
- [ ] Test `handle_newsletter_signup()`
- [ ] Test `track_view()` method

#### `apps/news_events/services.py` (12% coverage)
- [ ] Test article creation/update services
- [ ] Test event management services
- [ ] Test search functionality
- [ ] Test analytics services

### 2. Views (Medium Priority)
**Current Coverage: 18-55%**

#### `apps/contact/views.py` (26% coverage)
- [ ] Test contact form submission (success/failure)
- [ ] Test AJAX form submissions
- [ ] Test map views
- [ ] Test error handling

#### `apps/downloads/views.py` (18% coverage)
- [ ] Test download center with filters
- [ ] Test file download with various permissions
- [ ] Test bulk download functionality
- [ ] Test expired file handling

#### `apps/services/views.py` (25% coverage)
- [ ] Test service detail views
- [ ] Test service list views with filters
- [ ] Test API endpoints
- [ ] Test form submissions

### 3. Security & Middleware (High Priority)
**Current Coverage: 0-49%**

#### `apps/core/middleware.py` (49% coverage)
- [ ] Test `SecurityHeadersMiddleware`
- [ ] Test `RateLimitMiddleware`
- [ ] Test `InputValidationMiddleware`
- [ ] Test `BruteForceProtectionMiddleware`
- [ ] Test `PerformanceMonitoringMiddleware`

#### `apps/core/security_decorators.py` (0% coverage)
- [ ] Test all security decorators
- [ ] Test permission checks
- [ ] Test rate limiting decorators

#### `apps/downloads/security.py` (29% coverage)
- [ ] Test `AccessControlManager` methods
- [ ] Test file validation
- [ ] Test security audit logging
- [ ] Test rate limiting

### 4. Forms & Validation (Medium Priority)
**Current Coverage: 40-80%**

#### `apps/contact/forms.py` (40% coverage)
- [ ] Test all validation rules
- [ ] Test spam detection
- [ ] Test file upload validation
- [ ] Test edge cases

#### `apps/news_events/forms.py` (40% coverage)
- [ ] Test article form validation
- [ ] Test event form validation
- [ ] Test comment form validation

### 5. Utilities & Helpers (Low Priority)
**Current Coverage: 0-57%**

#### `apps/contact/utils/` (0% coverage)
- [ ] Test validators
- [ ] Test helpers
- [ ] Test constants usage

#### `apps/downloads/utils/` (0% coverage)
- [ ] Test utility functions
- [ ] Test constants

## Implementation Strategy

### Phase 1: Services Layer (Target: +10% coverage)
1. Start with `apps/home/services.py` (easiest, already 27%)
2. Move to `apps/about/services.py` (33% coverage)
3. Then `apps/contact/services.py` (0% coverage)
4. Finally `apps/downloads/services.py` (0% coverage)

### Phase 2: Security & Middleware (Target: +5% coverage)
1. Test middleware components
2. Test security decorators
3. Test access control managers

### Phase 3: Views & Forms (Target: +5% coverage)
1. Test view error handling
2. Test form validation edge cases
3. Test API endpoints

### Phase 4: Integration Tests (Target: +2% coverage)
1. Add end-to-end user flow tests
2. Test cross-app interactions
3. Test authentication flows

## Quick Wins

### Immediate Actions (Can add 5-10% quickly)
1. **Test services error handling** - Add try/except test cases
2. **Test form validation** - Add invalid input tests
3. **Test view edge cases** - Add 404, 403, 500 error tests
4. **Test API endpoints** - Add tests for all API views

## Testing Commands

```bash
# Run tests with coverage
pytest --cov=apps --cov-report=html --cov-report=term-missing

# Run tests for specific app
pytest apps/home/tests/ --cov=apps/home --cov-report=term-missing

# Run tests for specific file
pytest apps/home/services.py --cov=apps/home/services --cov-report=term-missing

# View HTML coverage report
# Open htmlcov/index.html in browser
```

## Success Metrics

- [ ] Reach 65% coverage (Phase 1 complete)
- [ ] Reach 70% coverage (Phase 2 complete)
- [ ] Reach 75% coverage (Phase 3 complete)
- [ ] Reach 80% coverage (Phase 4 complete)

## Notes

- Focus on testing business logic first (services)
- Security and middleware are critical for production
- Views can be tested with integration tests
- Utilities are lower priority but should be tested

