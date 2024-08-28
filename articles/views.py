from typing import Type

from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.authentications import CustomJWTAuthentication
from .filters import ArticleFilter
from .models import Article, TopicFollow, Topic, Comment
from .serializers import (
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    CommentSerializer,
    ArticleDetailCommentSerializer
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
    ,
    partial_update=extend_schema(
        summary="Update Article",
        request=ArticleCreateSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            404: "Article Does Not Exist"
        }
    )
)
class ArticlesView(viewsets.ModelViewSet):
    queryset: QuerySet = Article.objects.exclude(status="trash")
    filterset_class: Type[ArticleFilter] = ArticleFilter

    def get_permissions(self) -> list:
        if self.request.method in ('DELETE', 'POST'):
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_authenticators(self) -> list[CustomJWTAuthentication] | list:
        if self.request is not None and self.request.method == 'DELETE':
            return [CustomJWTAuthentication()]
        return []

    def get_serializer_class(self) -> Type[ArticleCreateSerializer] | Type[ArticleDetailSerializer] | Type[
        ArticleListSerializer]:
        if self.action in ('create', 'partial_update', 'update'):
            return ArticleCreateSerializer

        if self.action == 'list':
            return ArticleListSerializer

        return ArticleDetailSerializer

    def create(self, request: HttpRequest, *args, **kwargs) -> Response:
        create_serializer: ArticleCreateSerializer = self.get_serializer(data={**request.data, "author": request.user})

        if create_serializer.is_valid():
            article: Article = create_serializer.save()
            detail_serializer: ArticleDetailSerializer = ArticleDetailSerializer(article)
            return Response(data=detail_serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:

        article: Article | None = get_object_or_404(Article, pk=pk)

        if request.user != article.author:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        article.status = 'trash'
        article.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TopicFollowView(APIView):
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def post(self, request: HttpRequest, pk: int, *args, **kwargs):
        topic: Topic | None = Topic.objects.filter(pk=pk).first()

        if topic is None:
            return Response(
                data={"detail": "Hech qanday mavzu berilgan soʻrovga mos kelmaydi."},
                status=status.HTTP_404_NOT_FOUND
            )

        follow: TopicFollow | None = TopicFollow.objects.filter(user=request.user, topic=topic).first()

        if follow is not None:
            return Response(
                data={"detail": f"Siz allaqachon '{topic.name}' mavzusini kuzatyapsiz."},
                status=status.HTTP_200_OK
            )

        TopicFollow.objects.create(user=request.user, topic=topic)

        return Response(
            data={"detail": f"Siz '{topic.name}' mavzusini kuzatyapsiz."},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request: HttpRequest, pk: int, *args, **kwargs):
        topic: Topic | None = Topic.objects.filter(pk=pk).first()

        if topic is None:
            return Response(
                data={"detail": "Hech qanday mavzu berilgan soʻrovga mos kelmaydi."},
                status=status.HTTP_404_NOT_FOUND
            )

        follow: TopicFollow = TopicFollow.objects.filter(user=request.user, topic=topic).first()
        if not follow:
            return Response(
                data={"detail": f"Siz '{topic.name}' mavzusini kuzatmaysiz."},
                status=status.HTTP_404_NOT_FOUND
            )

        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateCommentsView(APIView):
    serializer_class: Type[CommentSerializer] = CommentSerializer
    queryset: QuerySet = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        article: Article = get_object_or_404(Article, pk=pk)

        if article.status == 'trash':
            return Response(data={"detail": "Article is deleted and cannot accept comments"},
                            status=status.HTTP_404_NOT_FOUND)
        data: dict[str, int | str] = {
            'user': request.user,
            'article': article.id,
            'content': request.data.get('content'),
            'parent': request.data.get('parent')
        }

        serializer: CommentSerializer = self.serializer_class(data=data)

        if serializer.is_valid():
            comment: Comment = serializer.save()

            comment_data: ArticleDetailCommentSerializer = ArticleDetailCommentSerializer(instance=comment)

            return Response(data=comment_data.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsView(viewsets.ModelViewSet):
    serializer_class: Type[CommentSerializer] = CommentSerializer
    queryset: QuerySet[Comment] = Comment.objects.all()

    def partial_update(self, request: HttpRequest, *args, **kwargs) -> Response:
        response: Response = super().partial_update(request, *args, **kwargs)

        article: Article = self.get_object()

        detail_serializer: ArticleDetailCommentSerializer = ArticleDetailCommentSerializer(article)

        return Response(detail_serializer.data, status=status.HTTP_200_OK)


class ArticleDetailCommentsView(ListAPIView):
    serializer_class: Type[ArticleDetailCommentSerializer] = ArticleDetailCommentSerializer

    def get_queryset(self) -> QuerySet[Comment]:
        article_id: int = self.kwargs.get('pk')
        return Comment.objects.filter(article_id=article_id)
