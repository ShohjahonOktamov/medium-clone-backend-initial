from django.contrib import admin

from .models import Topic, Article


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display: tuple[str, str] = ('id', 'name')
    list_display_links: tuple[str, str] = ('id', 'name')
    search_fields: tuple[str, str] = ('id', 'name')
    list_filter: tuple[str, str, str] = ('id', 'name', 'is_active')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display: tuple[str, str] = ('id', 'title', 'created_at', 'updated_at')
    list_display_links: tuple[str, str] = ('id', 'title')
    search_fields: tuple[str, str] = ('id', 'title')
    list_filter: tuple[str, str, str] = ('id', 'title', 'status')