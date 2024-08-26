from typing import Type

from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.response import Response

from .filters import ArticleFilter
from .models import Article
from .serializers import (
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List Articles",
        request=None,
        responses={
            200: ArticleListSerializer(many=True)
        }
    )
    ,
    retrieve=extend_schema(
        summary="Get Article Details",
        request=None,
        responses={
            200: ArticleDetailSerializer
        }
    ),
    create=extend_schema(
        summary="Create Article",
        request=ArticleCreateSerializer,
        responses={
            201: ArticleDetailSerializer
        }
    ),
    destroy=extend_schema(
        summary="Delete Article",
        request=None,
        responses={
            204: None,
            403: "Forbidden",
            404: "Article Does Not Exist"
        }
    )
)
class ArticlesView(viewsets.ModelViewSet):
    queryset: QuerySet = Article.objects.all()
    filterset_class: Type[ArticleFilter] = ArticleFilter

    def get_serializer_class(self) -> Type[ArticleCreateSerializer] | Type[ArticleDetailSerializer] | Type[
        ArticleListSerializer]:
        if self.action == 'create':
            return ArticleCreateSerializer

        if self.action == 'list':
            return ArticleListSerializer

        return ArticleDetailSerializer

    def create(self, request: HttpRequest, *args, **kwargs) -> Response:
        create_serializer: ArticleCreateSerializer = self.get_serializer(data=request.data)

        if create_serializer.is_valid():
            article: Article = create_serializer.save()
            detail_serializer: ArticleDetailSerializer = ArticleDetailSerializer(article)
            return Response(data=detail_serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: HttpRequest, pk: int, *args, **kwargs):
        article: Article | None = get_object_or_404(Article, pk=pk)
        print(request.user)
        if request.user != article.author:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        article.status = 'trash'
        article.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
