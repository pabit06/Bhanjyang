# Single initial migration - replaces 0001 through 0009

import apps.contact.models
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ('contact', '0001_initial'),
        ('contact', '0002_contactsubmission_attachment'),
        ('contact', '0003_add_indexes'),
        ('contact', '0004_kymsubmission'),
        ('contact', '0005_add_database_indexes'),
        ('contact', '0006_add_office_location_model'),
        ('contact', '0007_privacypolicy'),
        ('contact', '0008_faq'),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContactSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Full name of the person submitting the form", max_length=100)),
                ("email", models.EmailField(help_text="Email address for response", max_length=254)),
                ("phone", models.CharField(blank=True, help_text="Optional phone number", max_length=20)),
                ("subject", models.CharField(help_text="Subject of the inquiry", max_length=200)),
                ("message", models.TextField(help_text="Detailed message content")),
                (
                    "attachment",
                    models.FileField(
                        blank=True,
                        help_text="Optional file attachment",
                        null=True,
                        upload_to=apps.contact.models.contact_attachment_path,
                    ),
                ),
                ("ip_address", models.GenericIPAddressField(help_text="IP address of the submitter")),
                ("user_agent", models.TextField(blank=True, help_text="Browser user agent string")),
                ("created_at", models.DateTimeField(auto_now_add=True, help_text="When the submission was created")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="When the submission was last updated")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("in_progress", "In Progress"),
                            ("resolved", "Resolved"),
                            ("spam", "Spam"),
                        ],
                        default="new",
                        help_text="Current status of the submission",
                        max_length=20,
                    ),
                ),
                ("admin_notes", models.TextField(blank=True, help_text="Internal notes for admin use")),
                ("resolved_at", models.DateTimeField(blank=True, help_text="When the submission was resolved", null=True)),
            ],
            options={
                "verbose_name": "Contact Submission",
                "verbose_name_plural": "Contact Submissions",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["status", "created_at"], name="contact_con_status_57081e_idx"),
                    models.Index(fields=["email"], name="contact_con_email_394734_idx"),
                    models.Index(fields=["created_at"], name="contact_con_created_0e637d_idx"),
                    models.Index(fields=["ip_address"], name="contact_con_ip_addr_abc123_idx"),
                    models.Index(fields=["status"], name="contact_con_status2_def456_idx"),
                    models.Index(fields=["resolved_at"], name="contact_con_resolv_ghi789_idx"),
                    models.Index(fields=["name"], name="contact_con_name_jkl012_idx"),
                    models.Index(fields=["phone"], name="contact_con_phone_mno345_idx"),
                    models.Index(fields=["updated_at"], name="contact_con_updated_pqr678_idx"),
                    models.Index(fields=["subject"], name="contact_con_subject_stu901_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="OfficeLocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Name of the location (e.g., 'Main Office', 'Polyang Branch')", max_length=200)),
                ("address", models.CharField(help_text="Full address of the location", max_length=255)),
                ("latitude", models.DecimalField(decimal_places=6, help_text="Latitude coordinate for map display", max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, help_text="Longitude coordinate for map display", max_digits=9)),
                (
                    "location_type",
                    models.CharField(
                        choices=[
                            ("main_office", "Main Office"),
                            ("branch_office", "Branch Office"),
                            ("service_center", "Service Center"),
                            ("atm_center", "ATM Center"),
                        ],
                        default="branch_office",
                        help_text="Type of location",
                        max_length=20,
                    ),
                ),
                ("phone", models.CharField(blank=True, help_text="Contact phone number for this location", max_length=20)),
                ("email", models.EmailField(blank=True, help_text="Contact email for this location", max_length=254)),
                ("hours", models.CharField(blank=True, help_text="Operating hours (e.g., '9:00 AM - 5:00 PM', '24/7')", max_length=100)),
                ("description", models.TextField(blank=True, help_text="Description of the location and services offered")),
                ("image", models.ImageField(blank=True, help_text="Image of the location", null=True, upload_to="contact/locations/")),
                ("services", models.JSONField(blank=True, default=list, help_text="List of services offered at this location (e.g., ['Savings', 'Loans'])")),
                ("is_active", models.BooleanField(default=True, help_text="Whether this location is currently active")),
                ("order", models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first)")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Office Location",
                "verbose_name_plural": "Office Locations",
                "ordering": ["order", "name"],
                "indexes": [
                    models.Index(fields=["location_type", "is_active"], name="contact_off_locatio_208422_idx"),
                    models.Index(fields=["is_active", "order"], name="contact_off_is_acti_8f4d39_idx"),
                    models.Index(fields=["name"], name="contact_off_name_f62615_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="PrivacyPolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="Privacy Policy", max_length=200)),
                ("content", models.TextField(help_text="HTML content of the privacy policy")),
                ("version", models.CharField(default="1.0", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("last_updated", models.DateField(auto_now=True)),
            ],
            options={
                "verbose_name": "Privacy Policy",
                "verbose_name_plural": "Privacy Policies",
            },
        ),
        migrations.CreateModel(
            name="FAQ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.CharField(max_length=255, verbose_name="Question")),
                ("answer", models.TextField(verbose_name="Answer")),
                ("order", models.PositiveIntegerField(default=0, help_text="Order to display the FAQ (lowest first)", verbose_name="Order")),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "FAQ",
                "verbose_name_plural": "FAQs",
                "ordering": ["order", "created_at"],
            },
        ),
    ]
