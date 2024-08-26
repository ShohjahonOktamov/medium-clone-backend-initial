from typing import Type

import django_filters

from .models import Article


class ArticleFilter(django_filters.FilterSet):
    class Meta:
        model: Type[Article] = Article
        fields: str = "__all__"
