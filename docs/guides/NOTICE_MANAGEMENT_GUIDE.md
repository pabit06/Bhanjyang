# Notice Management Guide (सूचना व्यवस्थापन गाइड)

## 📋 Notice थप्ने तरिकाहरू

Notice (सूचना) थप्नका लागि तीनवटा तरिका छन्:

1. **News Events App मा Article को रूपमा** (Recommended) ✅
2. **Home App मा Announcement को रूपमा** (Simple)
3. **Dedicated Notice Model** (Advanced)

---

## 🎯 Method 1: News Events App मा Article (Recommended)

यो सबैभन्दा राम्रो तरिका हो किनकि:
- ✅ Complete CMS features
- ✅ Categories बाट organize गर्न सकिन्छ
- ✅ Priority levels (URGENT for important notices)
- ✅ Featured notices
- ✅ Search functionality
- ✅ API access
- ✅ Analytics tracking

### Step 1: Notice Category बनाउनुहोस्

**Admin Panel बाट:**
1. `/admin/news_events/category/` मा जानुहोस्
2. "Add Category" click गर्नुहोस्
3. यी details भरनुहोस्:
   - **Name**: "सूचनाहरू" (Notices)
   - **Slug**: "notices" (auto-generated)
   - **Description**: "Financial notices, AGM notices, interest rate changes"
   - **Color**: "#FF6B35" (orange for notices)
   - **Icon**: "fas fa-bullhorn"
   - **Is Active**: ✅ Checked
   - **Sort Order**: 1 (top position)

**Python Code बाट:**
```python
from apps.news_events.models import Category

# Notice category बनाउन
notice_category = Category.objects.create(
    name="सूचनाहरू",
    slug="notices",
    description="Financial notices, AGM notices, interest rate changes",
    color="#FF6B35",
    icon="fas fa-bullhorn",
    is_active=True,
    sort_order=1
)
```

### Step 2: Notice Article थप्नुहोस्

**Admin Panel बाट:**
1. `/admin/news_events/newsarticle/` मा जानुहोस्
2. "Add News Article" click गर्नुहोस्
3. यी details भरनुहोस्:

**Basic Information:**
- **Title**: "ब्याजदर परिवर्तन सूचना" (Interest Rate Change Notice)
- **Category**: "सूचनाहरू" (Notices) select गर्नुहोस्
- **Author**: आफ्नो user select गर्नुहोस्
- **Content**: Notice को full content
- **Excerpt**: Short summary (optional)

**Settings:**
- **Status**: "Published" (प्रकाशित)
- **Priority**: "URGENT" (तत्काल) - Important notices को लागि
- **Is Featured**: ✅ Checked (home page मा देखाउन)
- **Is Pinned**: ✅ Checked (top मा pin गर्न)

**Publishing:**
- **Published Date**: Today's date/time
- **Scheduled Date**: (optional) Future date मा publish गर्न

**Example Notice Types:**

#### 1. Interest Rate Change Notice
```
Title: "ब्याजदर परिवर्तन सूचना - २०८१"
Category: सूचनाहरू
Priority: URGENT
Content: 
हामीले निम्नलिखित ब्याजदर परिवर्तन गरेका छौं:
- Savings Account: ५.५% बाट ६% मा
- Fixed Deposit (१ वर्ष): ८% बाट ८.५% मा
- Fixed Deposit (२ वर्ष): ९% बाट ९.५% मा

यो परिवर्तन २०८१ माघ १ गते देखि लागू हुनेछ।
```

#### 2. AGM Notice
```
Title: "वार्षिक साधारण सभा (AGM) - २०८१"
Category: सूचनाहरू
Priority: HIGH
Content:
सबै सदस्यहरूलाई सूचना:

हामीले वार्षिक साधारण सभा (AGM) आयोजना गरेका छौं।

मिति: २०८१ फागुन १५ गते
समय: बिहान १०:०० बजे
स्थान: सहकारी कार्यालय

सभामा उपस्थित हुनुहोस्।
```

#### 3. Service Update Notice
```
Title: "नयाँ सेवा सुरुवात - Digital Banking"
Category: सूचनाहरू
Priority: MEDIUM
Content:
हामीले Digital Banking सेवा सुरु गरेका छौं।
अब तपाईं online बाटै:
- Account balance check गर्न सक्नुहुन्छ
- Fund transfer गर्न सक्नुहुन्छ
- Bill payment गर्न सक्नुहुन्छ
```

**Python Code बाट:**
```python
from apps.news_events.models import NewsArticle, Category
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Notice category पाउन
notice_category = Category.objects.get(slug='notices')

# Author (admin user)
author = User.objects.filter(is_staff=True).first()

# Interest Rate Change Notice थप्न
interest_notice = NewsArticle.objects.create(
    title="ब्याजदर परिवर्तन सूचना - २०८१",
    category=notice_category,
    author=author,
    content="""
    <h2>ब्याजदर परिवर्तन</h2>
    <p>हामीले निम्नलिखित ब्याजदर परिवर्तन गरेका छौं:</p>
    <ul>
        <li>Savings Account: ५.५% बाट ६% मा</li>
        <li>Fixed Deposit (१ वर्ष): ८% बाट ८.५% मा</li>
        <li>Fixed Deposit (२ वर्ष): ९% बाट ९.५% मा</li>
    </ul>
    <p>यो परिवर्तन २०८१ माघ १ गते देखि लागू हुनेछ।</p>
    """,
    excerpt="ब्याजदर परिवर्तन सूचना - २०८१",
    status=NewsArticle.Status.PUBLISHED,
    priority=NewsArticle.Priority.URGENT,
    is_featured=True,
    is_pinned=True,
    published_date=timezone.now()
)

# AGM Notice थप्न
agm_notice = NewsArticle.objects.create(
    title="वार्षिक साधारण सभा (AGM) - २०८१",
    category=notice_category,
    author=author,
    content="""
    <h2>वार्षिक साधारण सभा (AGM)</h2>
    <p>सबै सदस्यहरूलाई सूचना:</p>
    <p>हामीले वार्षिक साधारण सभा (AGM) आयोजना गरेका छौं।</p>
    <ul>
        <li><strong>मिति:</strong> २०८१ फागुन १५ गते</li>
        <li><strong>समय:</strong> बिहान १०:०० बजे</li>
        <li><strong>स्थान:</strong> सहकारी कार्यालय</li>
    </ul>
    <p>सभामा उपस्थित हुनुहोस्।</p>
    """,
    excerpt="वार्षिक साधारण सभा (AGM) - २०८१",
    status=NewsArticle.Status.PUBLISHED,
    priority=NewsArticle.Priority.HIGH,
    is_featured=True,
    is_pinned=True,
    published_date=timezone.now()
)
```

### Step 3: Notice View गर्न

**Frontend मा:**
- `/news-events/` - सबै notices देखाउँछ
- `/news-events/category/notices/` - Notice category मा सबै notices
- `/news-events/article/<slug>/` - Specific notice detail

**API बाट:**
```bash
# सबै notices
GET /api/v1/news-events/articles/?category=notices

# Featured notices
GET /api/v1/news-events/articles/featured/

# URGENT priority notices
GET /api/v1/news-events/articles/?priority=URGENT
```

---

## 🏠 Method 2: Home App मा Announcement (Simple)

यो simple तरिका हो quick notices को लागि।

### Step 1: Announcement Type बढाउनुहोस्

**Option A: Existing Types Use गर्नुहोस्**
- `service` - Service updates को लागि
- `general` - General notices को लागि

**Option B: Model Update गर्नुहोस्** (Code change required)

```python
# apps/home/models.py मा
announcement_type = models.CharField(
    max_length=20,
    choices=[
        ('general', _('General')),
        ('service', _('Service Update')),
        ('event', _('Event')),
        ('holiday', _('Holiday Notice')),
        ('maintenance', _('Maintenance')),
        ('interest_rate', _('Interest Rate Change')),  # NEW
        ('agm', _('AGM Notice')),  # NEW
        ('financial', _('Financial Notice')),  # NEW
    ],
    default='general'
)
```

### Step 2: Announcement थप्नुहोस्

**Admin Panel बाट:**
1. `/admin/home/announcement/` मा जानुहोस्
2. "Add Announcement" click गर्नुहोस्
3. Details भरनुहोस्:
   - **Title**: "ब्याजदर परिवर्तन"
   - **Content**: Notice content
   - **Announcement Type**: "Service Update" वा "General"
   - **Priority**: "High" वा "Urgent"
   - **Is Featured**: ✅ (home page मा देखाउन)
   - **Publish Date**: Today
   - **Expiry Date**: (optional) जब expire हुने

**Python Code:**
```python
from apps.home.models import Announcement
from django.utils import timezone

# Interest rate notice
Announcement.objects.create(
    title="ब्याजदर परिवर्तन सूचना",
    content="हामीले ब्याजदर परिवर्तन गरेका छौं...",
    announcement_type='service',
    priority='high',
    is_featured=True,
    publish_date=timezone.now()
)
```

---

## 🎯 Method 3: Dedicated Notice Model (Advanced)

यदि तपाईं dedicated notice system चाहनुहुन्छ, यो बनाउन सकिन्छ:

### Notice Model बनाउन

```python
# apps/news_events/models.py मा थप्नुहोस्

class Notice(models.Model):
    """Dedicated model for financial and official notices"""
    
    class NoticeType(models.TextChoices):
        INTEREST_RATE = 'INT_RATE', _('ब्याजदर परिवर्तन')
        AGM = 'AGM', _('वार्षिक साधारण सभा')
        EGM = 'EGM', _('असाधारण साधारण सभा')
        FINANCIAL = 'FIN', _('आर्थिक सूचना')
        SERVICE_UPDATE = 'SVC', _('सेवा अपडेट')
        REGULATORY = 'REG', _('नियामक सूचना')
        OTHER = 'OTH', _('अन्य')
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('न्यून')
        MEDIUM = 'MED', _('मध्यम')
        HIGH = 'HIGH', _('उच्च')
        URGENT = 'URG', _('तत्काल')
    
    # Basic fields
    title = models.CharField(max_length=200, verbose_name=_("शीर्षक"))
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    notice_type = models.CharField(max_length=10, choices=NoticeType.choices, default=NoticeType.OTHER)
    priority = models.CharField(max_length=6, choices=Priority.choices, default=Priority.MEDIUM)
    
    # Content
    content = models.TextField(verbose_name=_("सामग्री"))
    summary = models.TextField(blank=True, max_length=500, verbose_name=_("सारांश"))
    
    # Dates
    effective_date = models.DateField(verbose_name=_("लागू मिति"), help_text=_("जब यो notice लागू हुने"))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_("समाप्ति मिति"))
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Attachments
    attachment = models.FileField(upload_to='notices/', blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-effective_date']
        verbose_name = _("सूचना")
        verbose_name_plural = _("सूचनाहरू")
        indexes = [
            models.Index(fields=['notice_type', 'is_active']),
            models.Index(fields=['priority', 'effective_date']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_nepali(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False
```

---

## 📝 Recommended Approach

**सबैभन्दा राम्रो तरिका: News Events App मा Article use गर्नु**

**किन?**
1. ✅ Already complete CMS system छ
2. ✅ Categories बाट organize गर्न सकिन्छ
3. ✅ Priority levels (URGENT for important)
4. ✅ Featured र pinned features
5. ✅ Full API access
6. ✅ Analytics tracking
7. ✅ Search functionality
8. ✅ Image support
9. ✅ SEO features

---

## 🚀 Quick Start Guide

### 1. Notice Category बनाउनुहोस्

**Admin Panel:**
```
1. /admin/news_events/category/add/
2. Name: "सूचनाहरू"
3. Slug: "notices" (auto)
4. Save
```

### 2. Notice Article थप्नुहोस्

**Admin Panel:**
```
1. /admin/news_events/newsarticle/add/
2. Title: "ब्याजदर परिवर्तन सूचना"
3. Category: "सूचनाहरू" select गर्नुहोस्
4. Content: Notice content
5. Status: Published
6. Priority: URGENT (important को लागि)
7. Is Featured: ✅
8. Is Pinned: ✅
9. Save
```

### 3. Notice View गर्न

- **Website:** `/news-events/category/notices/`
- **API:** `/api/v1/news-events/articles/?category=notices`
- **Featured:** `/api/v1/news-events/articles/featured/`

---

## 💡 Best Practices

1. **Important Notices को लागि:**
   - Priority: URGENT
   - Is Featured: ✅
   - Is Pinned: ✅

2. **Notice Categories:**
   - "सूचनाहरू" (General Notices)
   - "आर्थिक सूचना" (Financial Notices)
   - "सभा सूचना" (Meeting Notices)

3. **Expiry Dates:**
   - AGM notices: Meeting date पछि expire
   - Interest rate changes: New rate effective date सम्म

4. **Content Format:**
   - Clear headings
   - Bullet points for lists
   - Important dates bold गर्नुहोस्
   - Contact information include गर्नुहोस्

---

## 📊 Notice Types Examples

### Interest Rate Change
- **Category:** सूचनाहरू
- **Priority:** URGENT
- **Title:** "ब्याजदर परिवर्तन सूचना - [Date]"
- **Content:** Old rate, new rate, effective date

### AGM Notice
- **Category:** सूचनाहरू
- **Priority:** HIGH
- **Title:** "वार्षिक साधारण सभा (AGM) - [Year]"
- **Content:** Date, time, location, agenda

### Service Update
- **Category:** सूचनाहरू
- **Priority:** MEDIUM
- **Title:** "सेवा अपडेट - [Service Name]"
- **Content:** What changed, how it affects users

---

## 🔗 Useful Links

- **Admin Panel:** `/admin/news_events/newsarticle/`
- **Categories:** `/admin/news_events/category/`
- **API Docs:** `/api/v1/news-events/docs/`
- **Frontend:** `/news-events/`

---

**Note:** यदि तपाईं dedicated Notice model चाहनुहुन्छ, मैले बनाउन सक्छु। तर current NewsArticle system पनि धेरै राम्रो छ notice management को लागि।

