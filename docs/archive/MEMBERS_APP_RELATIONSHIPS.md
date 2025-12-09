# Members App - File Relationships Diagram

**Quick Reference Guide for Understanding Dependencies**

## Relationship Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMBERS APP (ARCHIVED)                       │
│              docs/archive/members_app/members/                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ DEPENDENCIES
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   CONFIG     │      │   STATIC     │      │  TEMPLATES   │
│   FILES      │      │   FILES      │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│ config/settings.py                                          │
│ ├─ INSTALLED_APPS: 'apps.members' ❌ COMMENTED             │
│ ├─ MIDDLEWARE: members.* ❌ ALREADY COMMENTED              │
│ ├─ AUTH_USER_MODEL: 'members.MemberUser' ❌ COMMENTED      │
│ ├─ LOGIN_URL: '/members/login/' → '/admin/login/' ✅       │
│ └─ CBS_* settings: ✅ REMAIN (may be used elsewhere)       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ config/urls.py                                              │
│ └─ path('members/', include('apps.members.urls')) ❌        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ static/css/member-portal.css                                │
│ └─ Status: ⚠️ UNUSED (still in project)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ static/js/member-portal.js                                  │
│ └─ Status: ⚠️ UNUSED (still in project)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ templates/partials/_header.html                             │
│ └─ {% url 'members:member_login' %} ❌ ALREADY COMMENTED   │
└─────────────────────────────────────────────────────────────┘
```

## Direct Dependencies

### 1. Configuration Files
```
config/settings.py
├── INSTALLED_APPS
│   └── 'apps.members' ❌ REMOVED
├── MIDDLEWARE
│   ├── MemberAuthenticationMiddleware ❌ ALREADY DISABLED
│   ├── MemberActivityMiddleware ❌ ALREADY DISABLED
│   └── MemberSecurityMiddleware ❌ ALREADY DISABLED
├── AUTH_USER_MODEL
│   └── 'members.MemberUser' ❌ ALREADY DISABLED
└── Authentication URLs
    ├── LOGIN_URL: Changed ✅
    ├── LOGIN_REDIRECT_URL: Changed ✅
    └── LOGOUT_REDIRECT_URL: Changed ✅

config/urls.py
└── path('members/', include('apps.members.urls')) ❌ REMOVED
```

### 2. Static Files (Unused but Present)
```
static/
├── css/
│   └── member-portal.css ⚠️ UNUSED
└── js/
    └── member-portal.js ⚠️ UNUSED
```

### 3. Templates
```
templates/partials/_header.html
└── Member login link ❌ ALREADY COMMENTED
```

## Indirect References (No Impact)

### Files That Mention "members" But Don't Depend on App

```
apps/home/views.py
└── Uses "members" as variable name (committee memberships)
    └── No dependency on apps.members ✅

apps/services/models.py
└── Mentions "members" in docstrings only
    └── No dependency on apps.members ✅

apps/search/
└── No references found ✅

apps/about/
└── No references found ✅
```

## Database Relationships

```
Database Tables (if they exist):
├── members_member
├── members_memberregistration
├── members_kycdocument
├── members_ward
├── members_memberaccount
├── members_membertransaction
├── members_memberloan
└── members_membernotification

Status: ⚠️ Tables may still exist in database
Action: Create migrations to drop if needed
```

## CBS Integration

```
config/settings.py
├── CBS_API_URL ✅ REMAINS
├── CBS_API_KEY ✅ REMAINS
├── CBS_API_SECRET ✅ REMAINS
├── CBS_API_TIMEOUT ✅ REMAINS
├── CBS_API_RETRY_ATTEMPTS ✅ REMAINS
└── CBS_ENCRYPTION_KEY ✅ REMAINS

Reason: May be used by other apps in the future
```

## Change Summary

| Component | Status Before | Status After | Impact |
|-----------|--------------|--------------|--------|
| App in INSTALLED_APPS | Active | Archived | ✅ No impact (was template-only) |
| URL Routing | Active | Removed | ✅ No impact (not actively used) |
| Middleware | Disabled | Disabled | ✅ No change |
| Custom User Model | Disabled | Disabled | ✅ No change |
| Auth URLs | `/members/*` | `/admin/*` | ⚠️ Changed |
| Static CSS/JS | Present | Present (unused) | ⚠️ Can be removed |
| Database Tables | May exist | May exist | ⚠️ Can be dropped |
| Header Link | Commented | Commented | ✅ No change |

## Legend

- ✅ Active/Working
- ❌ Disabled/Removed
- ⚠️ Needs Attention
- 📁 File/Directory
- 🔗 Dependency/Reference

## Quick Actions

### To Completely Remove References:
1. ✅ App already archived
2. ⚠️ Remove `static/css/member-portal.css` (optional)
3. ⚠️ Remove `static/js/member-portal.js` (optional)
4. ⚠️ Drop database tables (if needed)
5. ⚠️ Remove CBS settings (if not needed elsewhere)

### To Restore:
1. Move app back: `mv docs/archive/members_app/members apps/members`
2. Uncomment in `config/settings.py`
3. Uncomment in `config/urls.py`
4. Run migrations
5. Resolve any conflicts

---

**See:** `MEMBERS_APP_ARCHIVE.md` for detailed documentation

