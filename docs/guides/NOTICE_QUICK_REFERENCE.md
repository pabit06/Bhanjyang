# Notice थप्ने Quick Reference (सूचना थप्ने त्वरित सन्दर्भ)

## 🚀 सबैभन्दा सजिलो तरिका

### Admin Panel बाट (Recommended)

1. **Admin Panel खोल्नुहोस्:**
   ```
   http://localhost:8000/admin/news_events/newsarticle/add/
   ```

2. **Notice Details भरनुहोस्:**
   - **Title**: "ब्याजदर परिवर्तन सूचना - २०८१"
   - **Category**: "सूचनाहरू" (यदि छैन भने पहिले category बनाउनुहोस्)
   - **Author**: आफ्नो user
   - **Content**: Notice को full content
   - **Excerpt**: Short summary (optional)
   - **Status**: Published
   - **Priority**: URGENT (important notices को लागि)
   - **Is Featured**: ✅ (home page मा देखाउन)
   - **Is Pinned**: ✅ (top मा pin गर्न)

3. **Save** click गर्नुहोस्

---

## 📝 Notice Types Examples

### 1. Interest Rate Change (ब्याजदर परिवर्तन)

**Admin Panel मा:**
```
Title: "ब्याजदर परिवर्तन सूचना - २०८१ माघ"
Category: सूचनाहरू
Priority: URGENT
Is Featured: ✅
Is Pinned: ✅

Content:
<h2>ब्याजदर परिवर्तन</h2>
<p>हामीले निम्नलिखित ब्याजदर परिवर्तन गरेका छौं:</p>
<ul>
    <li><strong>Savings Account:</strong> ५.५% बाट <strong>६%</strong> मा</li>
    <li><strong>Fixed Deposit (१ वर्ष):</strong> ८% बाट <strong>८.५%</strong> मा</li>
    <li><strong>Fixed Deposit (२ वर्ष):</strong> ९% बाट <strong>९.५%</strong> मा</li>
</ul>
<p><strong>लागू मिति:</strong> २०८१ माघ १ गते देखि</p>
```

### 2. AGM Notice (वार्षिक साधारण सभा)

**Admin Panel मा:**
```
Title: "वार्षिक साधारण सभा (AGM) - २०८१"
Category: सूचनाहरू
Priority: HIGH
Is Featured: ✅
Is Pinned: ✅

Content:
<h2>वार्षिक साधारण सभा (AGM)</h2>
<p>सबै सदस्यहरूलाई सूचना:</p>
<p>हामीले वार्षिक साधारण सभा (AGM) आयोजना गरेका छौं।</p>
<ul>
    <li><strong>मिति:</strong> २०८१ फागुन १५ गते</li>
    <li><strong>समय:</strong> बिहान १०:०० बजे</li>
    <li><strong>स्थान:</strong> सहकारी कार्यालय</li>
    <li><strong>Agenda:</strong> Annual report, financial statements, board election</li>
</ul>
<p>सभामा उपस्थित हुनुहोस्।</p>
```

### 3. Service Update (सेवा अपडेट)

**Admin Panel मा:**
```
Title: "नयाँ सेवा - Digital Banking"
Category: सूचनाहरू
Priority: MEDIUM
Is Featured: ✅

Content:
<h2>Digital Banking सेवा सुरु</h2>
<p>हामीले Digital Banking सेवा सुरु गरेका छौं।</p>
<p>अब तपाईं online बाटै:</p>
<ul>
    <li>Account balance check गर्न सक्नुहुन्छ</li>
    <li>Fund transfer गर्न सक्नुहुन्छ</li>
    <li>Bill payment गर्न सक्नुहुन्छ</li>
</ul>
<p>Visit: <a href="/services/digital/">Digital Services</a></p>
```

---

## 💻 Command Line बाट (Quick)

### Management Command Use गर्न

```bash
# Interest Rate Change Notice
python manage.py add_notice \
  --type interest_rate \
  --title "ब्याजदर परिवर्तन सूचना - २०८१" \
  --content "<h2>ब्याजदर परिवर्तन</h2><p>हामीले ब्याजदर परिवर्तन गरेका छौं...</p>" \
  --priority URGENT \
  --featured \
  --pinned

# AGM Notice
python manage.py add_notice \
  --type agm \
  --title "वार्षिक साधारण सभा (AGM) - २०८१" \
  --content "<h2>AGM</h2><p>मिति: २०८१ फागुन १५</p>" \
  --priority HIGH \
  --featured \
  --pinned
```

---

## 🐍 Python Code बाट

```python
from apps.news_events.models import NewsArticle, Category
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Category पाउन वा बनाउन
category, created = Category.objects.get_or_create(
    slug='notices',
    defaults={
        'name': 'सूचनाहरू',
        'description': 'Financial notices, AGM notices',
        'color': '#FF6B35',
        'icon': 'fas fa-bullhorn',
        'is_active': True,
        'sort_order': 1
    }
)

# Author (staff user)
author = User.objects.filter(is_staff=True).first()

# Interest Rate Notice थप्न
notice = NewsArticle.objects.create(
    title="ब्याजदर परिवर्तन सूचना - २०८१",
    category=category,
    author=author,
    content="<h2>ब्याजदर परिवर्तन</h2><p>Content here...</p>",
    excerpt="ब्याजदर परिवर्तन सूचना",
    status=NewsArticle.Status.PUBLISHED,
    priority=NewsArticle.Priority.URGENT,
    is_featured=True,
    is_pinned=True,
    published_date=timezone.now()
)

print(f"Notice created: {notice.get_absolute_url()}")
```

---

## 📍 Notice कहाँ देखिन्छ?

### Frontend:
- **All Notices:** `/news-events/category/notices/`
- **Featured Notices:** `/news-events/` (home page)
- **Specific Notice:** `/news-events/article/<slug>/`

### API:
- **All Notices:** `GET /api/v1/news-events/articles/?category=notices`
- **Featured:** `GET /api/v1/news-events/articles/featured/`
- **URGENT:** `GET /api/v1/news-events/articles/?priority=URGENT`

### Admin:
- **List:** `/admin/news_events/newsarticle/`
- **Add:** `/admin/news_events/newsarticle/add/`
- **Edit:** `/admin/news_events/newsarticle/<id>/change/`

---

## 🎯 Priority Guidelines

- **URGENT**: Interest rate changes, critical financial notices
- **HIGH**: AGM, EGM, important meetings
- **MEDIUM**: Service updates, general notices
- **LOW**: Minor updates, reminders

---

## ✅ Best Practices

1. **Important Notices:**
   - Priority: URGENT
   - Is Featured: ✅
   - Is Pinned: ✅

2. **Content Format:**
   - Clear headings (h2, h3)
   - Bullet points for lists
   - Important dates bold
   - Contact info included

3. **Categories:**
   - "सूचनाहरू" - General notices
   - "आर्थिक सूचना" - Financial notices
   - "सभा सूचना" - Meeting notices

---

**Quick Start:** Admin Panel → News Articles → Add → Fill details → Save ✅

