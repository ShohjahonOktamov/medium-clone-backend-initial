from typing import Type

from django.db.models import QuerySet
from django_filters import FilterSet, NumberFilter, BooleanFilter

from .models import Article


class ArticleFilter(FilterSet):
    class Meta:
        model: Type[Article] = Article
        exclude: list[str] = ["thumbnail"]

    get_top_articles: NumberFilter = NumberFilter(method='filter_top_articles')
    views_count: NumberFilter = NumberFilter(field_name='views_count')

    is_recommend: BooleanFilter = BooleanFilter(method="filter_recommend_articles")

    def filter_top_articles(self, queryset: QuerySet[Article], name: str, limit: int) -> QuerySet[Article]:
        return queryset.order_by('-views_count')[:limit]

    def filter_recommend_articles(self, queryset: QuerySet[Article], name: str, is_recommend: bool) -> QuerySet[
        Article]:
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

        if is_recommend:
            queryset: QuerySet[Article] = queryset.filter(
                topics__recommendation__recommendation_type='more'
            ).distinct()
            return queryset
