from django.contrib import admin
from .models import NewsArticle, Event, Subscriber, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'category', 'published_date')
    list_filter = ('status', 'author', 'category', 'published_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-status', '-published_date')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'content', 'image')}),
        ('Publication Details', {'fields': ('status', 'author', 'published_date')}),
    )
    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'author') or not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location')
    list_filter = ('event_date',)
    search_fields = ('title', 'description', 'location')

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
