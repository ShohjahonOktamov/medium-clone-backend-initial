from typing import Type

from django.db.models import QuerySet
from django_filters import FilterSet, NumberFilter

from .models import Article


class ArticleFilter(FilterSet):
    class Meta:
        model: Type[Article] = Article
        exclude: list[str] = ["thumbnail"]

    get_top_articles: NumberFilter = NumberFilter(method='filter_top_articles')
    views_count: NumberFilter = NumberFilter(field_name='views_count')

    def filter_top_articles(self, queryset: QuerySet[Article], name: str, limit: int) -> QuerySet[Article]:
        return queryset.order_by('-views_count')[:limit]
