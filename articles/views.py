import logging
from typing import Type

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.response import Response

logger = logging.getLogger(__name__)
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

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        logger.debug(f"List Response status code: {response.status_code}")
        logger.debug(f"List Response content: {response.data}")
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        logger.debug(f"Retrieve Response status code: {response.status_code}")
        logger.debug(f"Retrieve Response content: {response.data}")
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        logger.debug(f"Create Response status code: {response.status_code}")
        logger.debug(f"Create Response content: {response.data}")
        return Response(
            {
                'status_code': response.data
            }
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        logger.debug(f"Update Response status code: {response.status_code}")
        logger.debug(f"Update Response content: {response.data}")
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        logger.debug(f"Destroy Response status code: {response.status_code}")
        logger.debug(f"Destroy Response content: {response.data}")
        return response
