from typing import Type

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.response import Response

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

    def create(self, request, *args, **kwargs) -> Response:
        create_serializer = self.get_serializer(data=request.data)

        if create_serializer.is_valid():
            article = create_serializer.save()
            detail_serializer = ArticleDetailSerializer(article)
            return Response(data=detail_serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
