from django.contrib import admin
from .models import Person, Committee, Membership, Staff

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    autocomplete_fields = ['person']

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'bio')
    search_fields = ('full_name',)

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenure_bs', 'is_active', 'order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name', 'tenure_bs')}
    inlines = [MembershipInline]

# NEW Admin section for Staff
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Staff model.
    """
    list_display = ('person', 'position', 'is_active', 'order')
    list_filter = ('is_active',)
    list_editable = ('position', 'is_active', 'order')
    autocomplete_fields = ['person'] # Easy searching for people
    search_fields = ('person__full_name', 'position')
