# downloads/models.py

from django.db import models

class Download(models.Model):
    """
    A model to store information about downloadable files.
    """
    title = models.CharField(max_length=200, help_text="शीर्षक")
    description = models.TextField(blank=True, help_text="छोटो विवरण")
    file = models.FileField(upload_to='downloads/', help_text="अपलोड गर्ने फाइल")
    uploaded_at = models.DateTimeField(auto_now_add=True, help_text="अपलोड गरिएको मिति")
    file_type = models.CharField(
        max_length=10,
        blank=True,
        help_text="फाइलको प्रकार (उदाहरण: pdf, docx, xlsx)। यदि खाली छोडियो भने, फाइल एक्सटेन्सनबाट अनुमान गरिनेछ।"
    )

    class Meta:
        ordering = ['-uploaded_at'] # Sort by newest first
        verbose_name = "डाउनलोड फाइल"
        verbose_name_plural = "डाउनलोड फाइलहरू"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically set file_type based on file extension
        if it's not explicitly provided.
        """
        if not self.file_type and self.file:
            # Extract file extension from the file name
            extension = self.file.name.split('.')[-1].lower()
            self.file_type = extension
        super().save(*args, **kwargs)