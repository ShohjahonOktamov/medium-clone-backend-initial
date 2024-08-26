from django.contrib import admin

from .models import Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display: tuple[str, str] = ('id', 'name')
    list_display_links: tuple[str, str] = ('id', 'name')
    search_fields: tuple[str, str] = ('id', 'name')
    list_filter: tuple[str, str, str] = ('id', 'name', 'is_active')
