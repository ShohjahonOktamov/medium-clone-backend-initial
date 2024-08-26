from typing import Type

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from .models import Article
from .serializers import (
    ArticleCreateSerializer,
    ArticleDetailSerializer
)


@extend_schema_view(
    get=extend_schema(
        summary="Get Article Details",
        request=None,
        responses={
            200: ArticleDetailSerializer
        }
    ),
    post=extend_schema(
        summary="Create Article",
        request=ArticleCreateSerializer,
        responses={
            201: ArticleDetailSerializer
        }
    )
)
class ArticlesView(viewsets.ModelViewSet):
    queryset = Article.objects.all()

    def get_serializer_class(self) -> Type[ArticleCreateSerializer] | Type[ArticleDetailSerializer]:
        if self.action == 'create':
            return ArticleCreateSerializer
        return ArticleDetailSerializer
