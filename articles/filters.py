from typing import Type

from django.db.models import QuerySet, Q
from django_filters import FilterSet, NumberFilter, BooleanFilter, CharFilter

from users.models import CustomUser
from .models import Article


class ArticleFilter(FilterSet):
    class Meta:
        model: Type[Article] = Article
        exclude: list[str] = ["thumbnail"]

    get_top_articles: NumberFilter = NumberFilter(method='filter_top_articles')
    views_count: NumberFilter = NumberFilter(field_name='views_count')

    def filter_top_articles(self, queryset: QuerySet[Article], name: str, limit: int) -> QuerySet[Article]:
        return queryset.order_by('-views_count')[:limit]

    is_recommend: BooleanFilter = BooleanFilter(method="filter_recommend_articles")

    def filter_recommend_articles(self, queryset: QuerySet[Article], name: str, is_recommend: bool) -> QuerySet[
        Article]:
        if is_recommend:
            queryset: QuerySet[Article] = queryset.filter(
                topics__recommendation__recommendation_type='more'
            ).distinct()
            return queryset

    search: CharFilter = CharFilter(method='filter_search')

    def filter_search(self, queryset: QuerySet[Article], name: str, value: str) -> QuerySet[Article]:
        return queryset.filter(
            Q(title__icontains=value) |
            Q(summary__icontains=value) |
            Q(content__icontains=value) |
            Q(topics__name__icontains=value)
        ).distinct()

    is_user_favorites: BooleanFilter = BooleanFilter(method='get_user_favorites')

    def get_user_favorites(self, queryset: QuerySet[Article], name: str, is_user_favorites: str) -> QuerySet[Article]:
        user: CustomUser = self.request.user

        if is_user_favorites:
            queryset: QuerySet[Article] = queryset.filter(author__favorites__user=user).distinct()
            return queryset

        queryset: QuerySet[Article] = queryset.exclude(author__favorites__user=user).distinct()
        return queryset
