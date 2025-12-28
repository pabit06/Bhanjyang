from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse

from .constants import DEFAULT_RTI_EMAIL



class ContentManager(models.Manager):
    """Custom manager for content filtering"""
    def active(self):
        return self.get_queryset().filter(is_active=True)
    
    def featured(self):
        return self.active().filter(is_featured=True)

class CooperativeInfo(models.Model):

    """Model to store cooperative information and history"""
    
    # Basic Information
    cooperative_name = models.CharField(max_length=200, verbose_name=_("Cooperative Name"))
    cooperative_name_nepali = models.CharField(max_length=200, verbose_name=_("Cooperative Name (Nepali)"))
    slug = models.SlugField(max_length=250, unique=True, blank=True, help_text=_("URL-friendly identifier"))
    
    # Cooperative Details
    established_date = models.DateField(verbose_name=_("Established Date"))
    registration_number = models.CharField(max_length=100, verbose_name=_("Registration Number"))
    license_number = models.CharField(max_length=100, verbose_name=_("License Number"))
    
    # Contact Information
    address = models.TextField(verbose_name=_("Address"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    email = models.EmailField(verbose_name=_("Email"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    
    # Note: Information Officer is now managed through Staff model
    # Use Staff.get_information_officer() to get the designated officer
    
    # Mission, Vision, Values
    mission = models.TextField(verbose_name=_("Mission Statement"))
    vision = models.TextField(verbose_name=_("Vision Statement"))
    values = models.TextField(verbose_name=_("Core Values"))
    
    # Cooperative Description
    description = models.TextField(verbose_name=_("Cooperative Description"))
    description_nepali = models.TextField(blank=True, verbose_name=_("Cooperative Description (Nepali)"))
    
    # Our Story Section
    our_story = models.TextField(blank=True, verbose_name=_("Our Story"), help_text=_("Content for the 'Our Story' section on About Us page"))
    our_story_nepali = models.TextField(blank=True, verbose_name=_("Our Story (Nepali)"), help_text=_("Our Story content in Nepali"))
    our_story_image = models.ImageField(upload_to='about/cooperative/', blank=True, null=True, verbose_name=_("Our Story Image"), help_text=_("Image for the Our Story section on About Us page"))
    
    # Media
    logo = models.ImageField(upload_to='about/cooperative/', blank=True, null=True, verbose_name=_("Cooperative Logo"))
    featured_image = models.ImageField(upload_to='about/cooperative/', blank=True, null=True, verbose_name=_("Featured Image"))
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom Managers
    objects = ContentManager()
    
    class Meta:
        verbose_name = _("Cooperative Information")
        verbose_name_plural = _("Cooperative Information")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),  # For URL lookups
            models.Index(fields=['is_active']),  # For filtering active items
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['updated_at']),  # For date-based queries
            models.Index(fields=['cooperative_name']),  # For search
        ]
    
    def __str__(self):
        return self.cooperative_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.cooperative_name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('about:cooperative_detail', kwargs={'slug': self.slug})


class CooperativeTimeline(models.Model):
    """Model to store cooperative timeline events"""
    
    EVENT_TYPES = [
        ('milestone', _('Milestone')),
        ('achievement', _('Achievement')),
        ('expansion', _('Expansion')),
        ('award', _('Award')),
        ('partnership', _('Partnership')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("Event Title"))
    description = models.TextField(verbose_name=_("Event Description"))
    event_date = models.DateField(verbose_name=_("Event Date"))
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='milestone', verbose_name=_("Event Type"))
    
    # Media
    image = models.ImageField(upload_to='about/timeline/', blank=True, null=True, verbose_name=_("Event Image"))
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    
    # Status
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Event"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom Managers
    objects = ContentManager()

    class Meta:
        verbose_name = _("Timeline Event")
        verbose_name_plural = _("Timeline Events")
        ordering = ['-event_date', 'order']
        indexes = [
            models.Index(fields=['is_active', 'is_featured', '-event_date']),
            models.Index(fields=['event_type', 'is_active']),  # For filtering by event type
            models.Index(fields=['event_date']),  # For date-based queries
            models.Index(fields=['created_at']),  # For date-based queries
            models.Index(fields=['title']),  # For search
        ]
    
    def __str__(self):
        return f"{self.title} - {self.event_date}"


class CooperativeStatistic(models.Model):
    """Model to store cooperative statistics and metrics"""
    
    STATISTIC_TYPES = [
        ('members', _('Total Members')),
        ('deposits', _('Total Deposits')),
        ('loans', _('Total Loans Disbursed')),
        ('branches', _('Number of Branches')),
        ('employees', _('Number of Employees')),
        ('assets', _('Total Assets')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("Statistic Title"))
    value = models.CharField(max_length=100, verbose_name=_("Value"))
    unit = models.CharField(max_length=50, blank=True, verbose_name=_("Unit"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    statistic_type = models.CharField(max_length=20, choices=STATISTIC_TYPES, default='other', verbose_name=_("Statistic Type"))
    
    # Visual representation
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon Class"))
    color = models.CharField(max_length=20, default='deuraligreen', verbose_name=_("Color Theme"))
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    
    # Status
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Statistic"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom Managers
    objects = ContentManager()

    class Meta:
        verbose_name = _("Statistic")
        verbose_name_plural = _("Statistics")
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),  # For filtering
            models.Index(fields=['statistic_type', 'is_active']),  # For filtering by type
            models.Index(fields=['order']),  # For ordering
            models.Index(fields=['title']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
        ]
    
    def __str__(self):
        return f"{self.title}: {self.value} {self.unit}"


class CooperativeAffiliation(models.Model):
    """Model to store cooperative affiliations and partnerships"""
    
    AFFILIATION_TYPES = [
        ('regulatory', _('Regulatory Body')),
        ('association', _('Professional Association')),
        ('partnership', _('Partnership')),
        ('certification', _('Certification Body')),
        ('umbrella', _('Umbrella Organization')),
        ('cooperative_bank', _('Cooperative Bank')),
        ('other', _('Other')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_("Organization Name"))
    description = models.TextField(verbose_name=_("Description"))
    affiliation_type = models.CharField(max_length=20, choices=AFFILIATION_TYPES, default='association', verbose_name=_("Affiliation Type"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    
    # Media
    logo = models.ImageField(upload_to='about/affiliations/', blank=True, null=True, verbose_name=_("Organization Logo"))
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    
    # Status
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Affiliation"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom Managers
    objects = ContentManager()

    class Meta:
        verbose_name = _("Affiliation")
        verbose_name_plural = _("Affiliations")
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),  # For filtering
            models.Index(fields=['affiliation_type', 'is_active']),  # For filtering by type
            models.Index(fields=['order']),  # For ordering
            models.Index(fields=['name']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
        ]
    
    def __str__(self):
        return self.name


class LeadershipMessage(models.Model):
    """Model to store leadership messages"""
    
    MESSAGE_TYPES = [
        ('chairman', _('Chairman Message')),
        ('manager', _('Manager Message')),
        ('director', _('Director Message')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("Message Title"))
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='other', verbose_name=_("Message Type"))
    content = models.TextField(verbose_name=_("Message Content"))
    author_name = models.CharField(max_length=100, verbose_name=_("Author Name"))
    author_position = models.CharField(max_length=100, verbose_name=_("Author Position"))
    
    # Media
    author_photo = models.ImageField(upload_to='about/leadership/', blank=True, null=True, verbose_name=_("Author Photo"))
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    
    # Status
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured Message"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom Managers
    objects = ContentManager()

    class Meta:
        verbose_name = _("Leadership Message")
        verbose_name_plural = _("Leadership Messages")
        ordering = ['order', 'message_type']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),  # For filtering
            models.Index(fields=['message_type', 'is_active']),  # For filtering by type
            models.Index(fields=['order']),  # For ordering
            models.Index(fields=['title']),  # For search
            models.Index(fields=['author_name']),  # For search
            models.Index(fields=['created_at']),  # For date-based queries
        ]
    
    def __str__(self):
        return f"{self.title} - {self.author_name}"


# Team Models (moved from team app)
class Person(models.Model):
    """Represents a unique person in the cooperative"""
    full_name = models.CharField(max_length=100, unique=True, help_text="व्यक्तिको पूरा नाम")
    photo = models.ImageField(upload_to='about/team/photos/', blank=True, null=True, help_text="व्यक्तिको फोटो")
    bio = models.TextField(blank=True, help_text="व्यक्तिको संक्षिप्त परिचय (optional)")
    
    # Additional fields for better integration
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    position_general = models.CharField(max_length=100, blank=True, verbose_name=_("General Position"))
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        indexes = [
            models.Index(fields=['full_name']),  # For search
            models.Index(fields=['is_active']),  # For filtering
            models.Index(fields=['email']),  # For email lookups
            models.Index(fields=['created_at']),  # For date-based queries
        ]

    def __str__(self):
        return self.full_name


class Committee(models.Model):
    """Represents a specific committee for a specific tenure"""
    name = models.CharField(max_length=150, help_text="e.g., सञ्चालक समिति, लेखा समिति")
    tenure_bs = models.CharField(max_length=20, help_text="e.g., २०८०-२०८३")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from name and tenure")
    is_active = models.BooleanField(default=True, help_text="Check this for the currently active committees.")
    order = models.PositiveIntegerField(default=0, help_text="Display order (e.g., 1 for Board, 2 for Audit).")
    
    # Additional fields for better integration
    description = models.TextField(blank=True, verbose_name=_("Committee Description"))
    photo = models.ImageField(upload_to='about/committees/', blank=True, null=True, verbose_name=_("Committee Photo"), help_text="Group photo or representative image of the committee")
    start_date = models.DateField(blank=True, null=True, verbose_name=_("Start Date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))

    class Meta:
        ordering = ['-is_active', 'order']
        verbose_name = _("Committee")
        verbose_name_plural = _("Committees")
        indexes = [
            models.Index(fields=['slug']),  # For URL lookups
            models.Index(fields=['is_active', 'order']),  # For filtering and ordering
            models.Index(fields=['name']),  # For search
            models.Index(fields=['tenure_bs']),  # For filtering by tenure
        ]

    def __str__(self):
        return f"{self.name} ({self.tenure_bs})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.tenure_bs}")
        super().save(*args, **kwargs)


class Membership(models.Model):
    """Links a Person to a Committee"""
    
    POSITION_CHOICES = [
        ('', _('Select Position')),
        # Board Positions
        ('chairman', _('Chairman')),
        ('vice_chairman', _('Vice-Chairman')),
        ('secretary', _('Secretary')),
        ('treasurer', _('Treasurer')),
        ('member', _('Member')),
        # Account Supervisor Committee Positions
        ('coordinator', _('Coordinator')),
        # Other positions (can be entered as free text)
        ('other', _('Other')),
    ]
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="memberships")
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name="memberships")
    position = models.CharField(
        max_length=100, 
        choices=POSITION_CHOICES,
        blank=True,
        help_text="Select standard position or enter custom position below"
    )
    position_custom = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Enter custom position if 'Other' is selected above (e.g., अध्यक्ष, सदस्य, ऋण संयोजक)"
    )
    order = models.PositiveIntegerField(default=0, help_text="Order within the committee (e.g., 1 for Chairman, 2 for Vice-Chairman).")
    
    # Additional fields
    start_date = models.DateField(blank=True, null=True, verbose_name=_("Start Date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        ordering = ['committee', 'order']
        unique_together = ('person', 'committee')
        verbose_name = _("Committee Membership")
        verbose_name_plural = _("Committee Memberships")
        indexes = [
            models.Index(fields=['committee', 'order']),  # For committee-based queries
            models.Index(fields=['person', 'committee']),  # For unique lookup optimization
            models.Index(fields=['is_active']),  # For filtering
            models.Index(fields=['position']),  # For filtering by position
        ]

    @property
    def position_display(self):
        """Get display name for position (accessible in templates)"""
        # If standard position selected (not 'other' and not empty), use it
        if self.position and self.position != 'other':
            # Use Django's built-in get_FOO_display() for choices
            return dict(self.POSITION_CHOICES).get(self.position, self.position)
        
        # If 'other' is selected, use custom if available
        if self.position == 'other' and self.position_custom:
            return self.position_custom
            
        # Fallback for empty position (legacy)
        if not self.position and self.position_custom:
            return self.position_custom
            
        return "Member"
    
    def __str__(self):
        person_name = "Unknown"
        committee_name = "Unknown Committee"
        
        try:
            if self.person_id:
                person_name = self.person.full_name
        except Exception:
            pass
        
        try:
            if self.committee_id:
                committee_name = str(self.committee)
        except Exception:
            pass
        
        return f"{person_name} - {self.position_display} of {committee_name}"


class Staff(models.Model):
    """Represents a Staff Member"""
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="staff_profile")
    position = models.CharField(max_length=100, help_text="e.g., Manager, Accountant")
    start_date = models.DateField(null=True, blank=True, help_text="Date the staff member joined.")
    is_active = models.BooleanField(default=True, help_text="Is the staff member currently employed?")
    order = models.PositiveIntegerField(default=0, help_text="Display order (e.g., 1 for Manager, 2 for others).")
    
    # Additional fields
    department = models.CharField(max_length=100, blank=True, verbose_name=_("Department"))
    salary_range = models.CharField(max_length=50, blank=True, verbose_name=_("Salary Range"))
    qualifications = models.TextField(blank=True, verbose_name=_("Qualifications"))
    
    # RTI Act 2064 - Information Officer Role
    is_information_officer = models.BooleanField(
        default=False,
        verbose_name=_("Information Officer (सूचना अधिकारी)"),
        help_text=_("Designate this staff member as the Information Officer under RTI Act 2064")
    )
    information_officer_email = models.EmailField(
        blank=True,
        default='',
        verbose_name=_("RTI Email"),
        help_text=_("Dedicated email for RTI requests (e.g., rti@bhanjyang.coop.np)")
    )

    class Meta:
        ordering = ['order']
        verbose_name = _("Staff Member")
        verbose_name_plural = _("Staff Members")
        indexes = [
            models.Index(fields=['person']),  # For person lookups
            models.Index(fields=['is_active', 'order']),  # For filtering and ordering
            models.Index(fields=['position']),  # For filtering by position
            models.Index(fields=['department']),  # For filtering by department
        ]

    def __str__(self):
        return f"{self.person.full_name} - {self.position}"
    
    def save(self, *args, **kwargs):
        """Ensure only one Information Officer is active at a time"""
        if self.is_information_officer and self.is_active:
            # Deactivate other Information Officers
            Staff.objects.filter(
                is_information_officer=True,
                is_active=True
            ).exclude(pk=self.pk).update(is_information_officer=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_information_officer(cls):
        """
        Get the current active Information Officer.
        
        Returns:
            Staff: The active Information Officer or None
        """
        return cls.objects.filter(
            is_information_officer=True,
            is_active=True
        ).select_related('person').first()
    
    def get_rti_email(self):
        """Get the RTI email - use dedicated email or fallback to person's email"""
        return self.information_officer_email or self.person.email or DEFAULT_RTI_EMAIL
