from typing import Type, Any

from django.contrib.auth.models import AnonymousUser
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
from users.models import CustomUser
from users.serializers import UserSerializer
from .filters import ArticleFilter
from .models import Article, TopicFollow, Topic, Comment, Favorite, Clap
from .serializers import (
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    CommentSerializer,
    ArticleDetailCommentsSerializer,
    ClapSerializer
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
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def get_permissions(self) -> list:
        if self.request.method in ('DELETE', 'POST'):
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

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

        if not request.user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

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
    queryset: QuerySet[Comment] = Comment.objects.all()
    permission_classes: list[Type[IsAuthenticated]] = [IsAuthenticated]
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        article: Article = get_object_or_404(Article, pk=pk)

        if article.status != 'publish':
            return Response(data={"detail": "Article is deleted and cannot accept comments"},
                            status=status.HTTP_404_NOT_FOUND)
        data: dict[str, int | str] = {
            'user': request.user.id,
            'article': article.id,
            'content': request.data.get('content'),
            'parent': request.data.get('parent')
        }

        serializer: CommentSerializer = self.serializer_class(data=data)

        if serializer.is_valid():
            comment: Comment = serializer.save()

            comment_data: ArticleDetailCommentsSerializer = ArticleDetailCommentsSerializer(instance=comment)

            return Response(data=comment_data.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsView(viewsets.ModelViewSet):
    serializer_class: Type[CommentSerializer] = CommentSerializer
    queryset: QuerySet[Comment] = Comment.objects.all()
    permission_classes: list[Type[IsAuthenticated]] = [IsAuthenticated]
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def partial_update(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        if not request.user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        comment: Comment = get_object_or_404(Comment, pk=pk)

        if request.user != comment.user:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        response: Response = super().partial_update(request, *args, **kwargs)

        article: Article = self.get_object()

        detail_serializer: ArticleDetailCommentsSerializer = ArticleDetailCommentsSerializer(article)

        return Response(detail_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        comment: Comment = get_object_or_404(Comment, pk=pk)

        if not request.user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if request.user != comment.user:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request=request, *args, **kwargs)


class ArticleDetailCommentsView(ListAPIView):
    serializer_class: Type[ArticleDetailCommentsSerializer] = ArticleDetailCommentsSerializer

    def get_queryset(self) -> QuerySet[Comment]:
        article_id: int = self.kwargs.get('pk')
        return Comment.objects.filter(article_id=article_id)

    def list(self, request, *args, **kwargs):
        queryset: QuerySet[Comment] = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer: ArticleDetailCommentsSerializer = self.get_serializer(page, many=True)
            paginated_data: Response = self.get_paginated_response(serializer.data).data

            data: dict = {
                "count": paginated_data["count"],
                "next": paginated_data["next"],
                "previous": paginated_data["previous"],
                "results": [
                    {
                        "comments": paginated_data["results"]
                    }
                ]
            }

            return Response(data)

        serializer: ArticleDetailCommentsSerializer = self.get_serializer(queryset, many=True)
        data: dict = {
            "results": [
                {
                    "comments": serializer.data
                }
            ]
        }
        return Response(data)


class FavoriteArticleView(APIView):
    queryset: QuerySet[Favorite] = Favorite.objects.all()

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        if not request.user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        article: Article = Article.objects.filter(pk=pk, status="publish").first()

        if article is not None:
            favorite: Favorite | None = Favorite.objects.filter(user=request.user, article=article).first()

            if favorite is None:
                Favorite.objects.create(user=request.user, article=article)

                return Response(data={
                    "detail": "Maqola sevimlilarga qo'shildi."
                }, status=status.HTTP_201_CREATED)

            return Response(data={
                "detail": "Maqola sevimlilarga allaqachon qo'shilgan."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={
            "detail": "Maqola topilmadi."
        }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        if not request.user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        article: Article = Article.objects.filter(pk=pk, status="publish").first()

        if article is not None:
            favorite: Favorite | None = Favorite.objects.filter(user=request.user, article=article).first()

            if favorite is not None:
                favorite.delete()

                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(data={"Maqola foydalanuvchining sevimlilariga qo'shilmagan."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(data={
            "detail": "Maqola topilmadi."
        }, status=status.HTTP_404_NOT_FOUND)


class ClapView(APIView):
    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        user: CustomUser | AnonymousUser = request.user

        if not user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        article: Article = get_object_or_404(Article, pk=pk)

        clap: Clap = Clap.objects.get_or_create(user=user, article=article)[0]

        if clap.count >= 50:
            return Response(data={'detail': 'Maximum clap limit reached for this article.'},
                            status=status.HTTP_201_CREATED)

        clap.count += 1

        serializer: ClapSerializer = ClapSerializer(instance=clap, data={'count': clap.count}, partial=True)

        if serializer.is_valid():
            serializer.save()

            data: dict[str, Any] = {
                'user': UserSerializer(user).data,
                'article': article.pk,
                'count': serializer.data['count']
            }

            return Response(data=data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        user: CustomUser | AnonymousUser = request.user

        if not user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        article: Article = get_object_or_404(Article, pk=pk)

        clap: Clap = get_object_or_404(Clap, article=article, user=user)

        clap.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
