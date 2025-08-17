from django.db import models
from django.utils.text import slugify

# Model 1: Represents a unique person. (No changes here)
class Person(models.Model):
    full_name = models.CharField(max_length=100, unique=True, help_text=" व्यक्तिको पूरा नाम")
    photo = models.ImageField(upload_to='person_photos/', blank=True, null=True, help_text=" व्यक्तिको फोटो")
    bio = models.TextField(blank=True, help_text=" व्यक्तिको संक्षिप्त परिचय (optional)")

    class Meta:
        ordering = ['full_name']
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return self.full_name

# Model 2: Represents a specific committee for a specific tenure. (No changes here)
class Committee(models.Model):
    name = models.CharField(max_length=150, help_text="e.g., सञ्चालक समिति, लेखा समिति")
    tenure_bs = models.CharField(max_length=20, help_text="e.g., २०८०-२०८३")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from name and tenure")
    is_active = models.BooleanField(default=True, help_text="Check this for the currently active committees.")
    order = models.PositiveIntegerField(default=0, help_text="Display order (e.g., 1 for Board, 2 for Audit).")

    class Meta:
        ordering = ['-is_active', 'order']
        verbose_name = "Committee"
        verbose_name_plural = "Committees"

    def __str__(self):
        return f"{self.name} ({self.tenure_bs})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.tenure_bs}")
        super().save(*args, **kwargs)

# Model 3: Links a Person to a Committee. (No changes here)
class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="memberships")
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name="memberships")
    position = models.CharField(max_length=100, help_text="e.g., अध्यक्ष, सदस्य, ऋण संयोजक")
    order = models.PositiveIntegerField(default=0, help_text="Order within the committee (e.g., 1 for President, 2 for VP).")

    class Meta:
        ordering = ['committee', 'order']
        unique_together = ('person', 'committee')
        verbose_name = "Committee Membership"
        verbose_name_plural = "Committee Memberships"

    def __str__(self):
        return f"{self.person.full_name} - {self.position} of {self.committee}"

# NEW Model 4: Represents a Staff Member.
# (कर्मचारीहरूको लागि छुट्टै model)
class Staff(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="staff_profile")
    position = models.CharField(max_length=100, help_text="e.g., Manager, Accountant")
    start_date = models.DateField(null=True, blank=True, help_text="Date the staff member joined.")
    is_active = models.BooleanField(default=True, help_text="Is the staff member currently employed?")
    order = models.PositiveIntegerField(default=0, help_text="Display order (e.g., 1 for Manager, 2 for others).")

    class Meta:
        ordering = ['order']
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"

    def __str__(self):
        return f"{self.person.full_name} - {self.position}"
