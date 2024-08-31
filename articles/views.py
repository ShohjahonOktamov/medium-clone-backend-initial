from typing import Type, Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.authentications import CustomJWTAuthentication
from users.models import CustomUser, ReadingHistory, Pin
from users.serializers import UserSerializer, PinSerializer
from .filters import ArticleFilter
from .models import Article, TopicFollow, Topic, Comment, Favorite, Clap, Report, FAQ
from .schemas import articles_list_response, unauthorized_response, article_detail_response, \
    no_article_matches_response, bad_request_response, no_content_response, forbidden_response, article_read_response, \
    article_archived, article_pin, article_already_pinned, article_not_found
from .serializers import (
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    CommentSerializer,
    ArticleDetailCommentsSerializer,
    ClapSerializer,
    FAQSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List Articles",
        request=None,
        responses={
            200: articles_list_response,
            401: unauthorized_response
        }
    ),
    retrieve=extend_schema(
        summary="Get Article Details",
        request=None,
        responses={
            200: article_detail_response,
            404: no_article_matches_response,
            401: unauthorized_response
        }
    ),
    create=extend_schema(
        summary="Create Article",
        request=ArticleCreateSerializer,
        responses={
            201: article_detail_response,
            400: bad_request_response,
            401: unauthorized_response
        }
    ),
    destroy=extend_schema(
        summary="Delete Article",
        request=None,
        responses={
            204: no_content_response,
            403: forbidden_response,
            404: no_article_matches_response,
            401: unauthorized_response
        }
    ),
    partial_update=extend_schema(
        summary="Update Article",
        request=ArticleCreateSerializer,
        responses={
            200: article_detail_response,
            400: bad_request_response,
            404: no_article_matches_response
        }
    ),
    read=extend_schema(
        summary="Increments article reads count",
        request=None,
        responses={
            200: article_read_response,
            404: no_article_matches_response
        }
    ),
    archive=extend_schema(
        summary="Archives article",
        request=None,
        responses={
            200: article_archived,
            404: no_article_matches_response,
            403: forbidden_response,
            401: unauthorized_response
        }
    ),
    pin=extend_schema(
        summary="Pins article",
        request=PinSerializer,
        responses={
            200: article_pin,
            404: no_article_matches_response,
            400: article_already_pinned,
            403: forbidden_response,
            401: unauthorized_response
        }
    ),
    unpin=extend_schema(
        summary="Unpins article",
        request=PinSerializer,
        responses={
            204: no_content_response,
            404: article_not_found,
            401: unauthorized_response,
            403: forbidden_response
        }
    )
)
class ArticlesView(viewsets.ModelViewSet):
    filterset_class: Type[ArticleFilter] = ArticleFilter
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def get_permissions(self) -> list:
        if self.action in ('destroy', 'create', 'retrieve', 'archive', 'pin', 'unpin'):
            self.permission_classes: tuple[Type[IsAuthenticated]] = IsAuthenticated,
        else:
            self.permission_classes: tuple[Type[AllowAny]] = AllowAny,
        return super().get_permissions()

    def get_serializer_class(self) -> Type[ArticleCreateSerializer] | Type[ArticleDetailSerializer] | Type[
        ArticleListSerializer] | Type[PinSerializer]:
        if self.action in ('create', 'partial_update', 'update'):
            return ArticleCreateSerializer

        if self.action == 'list':
            return ArticleListSerializer

        if self.action == 'retrieve':
            return ArticleDetailSerializer

        if self.action in ('pin', 'unpin'):
            return PinSerializer

        return None

    def create(self, request: HttpRequest, *args, **kwargs) -> Response:
        create_serializer: ArticleCreateSerializer = self.get_serializer(data={**request.data, "author": request.user})

        if create_serializer.is_valid():
            article: Article = create_serializer.save()
            detail_serializer: ArticleDetailSerializer = ArticleDetailSerializer(article)
            return Response(data=detail_serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:

        article: Article | None = get_object_or_404(klass=self.get_queryset(), pk=pk)

        if not request.user.is_authenticated:
            return Response(data={'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if request.user != article.author:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        article.status = 'trash'
        article.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request: HttpRequest, pk: int, *args, **kwargs):
        article: Article = get_object_or_404(klass=self.get_queryset(), pk=pk)

        user: CustomUser = request.user

        if not ReadingHistory.objects.filter(user=user, article=article).exists():
            ReadingHistory.objects.create(user=user, article=article)

            article.views_count += 1
            article.save()

        return super().retrieve(request=request, *args, **kwargs)

    @action(methods=["POST"], detail=True, description="Increments article reads count", url_path="read",
            url_name="article-read")
    def read(self, request: HttpRequest, pk: int, *args, **kwargs):
        article: Article = get_object_or_404(klass=self.get_queryset(), pk=pk)

        article.reads_count += 1
        article.save()

        return Response(data={
            "detail": "Maqolani o'qish soni ortdi."
        }
            , status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, description="Archives article", url_path="archive",
            url_name="article-archive")
    def archive(self, request: HttpRequest, pk: int, *args, **kwargs):
        article: Article = get_object_or_404(klass=self.get_queryset(), pk=pk)

        if request.user != article.author:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        article.status = "archive"
        article.save()

        return Response(data={
            "detail": "Maqola arxivlandi."
        }, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, description="Pins article", url_path="pin",
            url_name="article-pin")
    def pin(self, request: HttpRequest, pk: int, *args, **kwargs):
        article: Article = get_object_or_404(klass=self.get_queryset(), pk=pk)

        if Pin.objects.filter(article=article).exists():
            return Response(data={"detail": "Maqola allaqachon pin qilingan."}, status=status.HTTP_400_BAD_REQUEST)

        Pin.objects.create(article=article)

        return Response(data={
            "detail": "Maqola pin qilindi."
        }, status=status.HTTP_200_OK)

    @action(methods=["DELETE"], detail=True, description="Unpins article", url_path="unpin",
            url_name="article-unpin")
    def unpin(self, request: HttpRequest, pk: int, *args, **kwargs):
        article: Article = self.get_queryset().filter(pk=pk).first()

        if article is None:
            return Response(data={"detail": "Maqola topilmadi.."}, status=status.HTTP_404_NOT_FOUND)

        pin: Pin = Pin.objects.filter(article=article).first()

        if pin is None:
            return Response(data={"detail": "Maqola topilmadi.."}, status=status.HTTP_404_NOT_FOUND)

        pin.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self) -> QuerySet[Article]:
        if self.action in ('retrieve', 'list', 'destroy', 'create'):
            return Article.objects.exclude(status__in=("trash", "archive"))
        return Article.objects.filter(status="publish")


@extend_schema_view(
    post=extend_schema(
        summary="Topic Follow",
        request=None,
        responses={
            404: "Hech qanday mavzu berilgan soʻrovga mos kelmaydi.",
            200: "Siz allaqachon '{topic}' mavzusini kuzatyapsiz.",
            201: "Siz '{topic}' mavzusini kuzatyapsiz."
        }
    ),
    delete=extend_schema(
        summary="Topic Unfollow",
        request=None,
        responses={
            404: "Hech qanday mavzu berilgan soʻrovga mos kelmaydi./Siz '{topic}' mavzusini kuzatmaysiz.",
            204: no_content_response
        }
    )
)
class TopicFollowView(APIView):
    permission_classes: tuple[Type[IsAuthenticated]] = IsAuthenticated,
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def post(self, request: HttpRequest, pk: int, *args, **kwargs):
        topic: Topic | None = Topic.objects.filter(pk=pk).first()

        if topic is None:
            return Response(
                data={"detail": "Hech qanday mavzu berilgan soʻrovga mos kelmaydi."},
                status=status.HTTP_404_NOT_FOUND
            )

        user: CustomUser = request.user

        if TopicFollow.objects.filter(user=user, topic=topic).exists():
            return Response(
                data={"detail": f"Siz allaqachon '{topic.name}' mavzusini kuzatyapsiz."},
                status=status.HTTP_200_OK
            )

        TopicFollow.objects.create(user=user, topic=topic)

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

        user: CustomUser = request.user

        follow: TopicFollow = TopicFollow.objects.filter(user=user, topic=topic).first()

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
    permission_classes: tuple[Type[IsAuthenticated]] = IsAuthenticated,
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    @extend_schema(
        summary="Article Comment Create",
        request=CommentSerializer,
        responses={
            201: ArticleDetailCommentsSerializer,
            404: "Article is deleted and cannot accept comments",
            400: "Bad Request."
        }
    )
    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        article: Article = get_object_or_404(klass=self.get_articles_queryset(), pk=pk)

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

    def get_articles_queryset(self) -> QuerySet[Article]:
        return Article.objects.filter(status="publish")


class CommentsView(viewsets.ModelViewSet):
    serializer_class: Type[CommentSerializer] = CommentSerializer
    queryset: QuerySet[Comment] = Comment.objects.all()

    permission_classes: tuple[Type[IsAuthenticated]] = IsAuthenticated,
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    @extend_schema(
        summary="Update Comment",
        request=CommentSerializer,
        responses={
            200: ArticleDetailCommentsSerializer,
            401: unauthorized_response,
            403: forbidden_response,
            404: "No Comment matches the given query."
        }
    )
    def partial_update(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        user: CustomUser = request.user

        comment: Comment = get_object_or_404(Comment, pk=pk)

        if user != comment.user:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        response: Response = super().partial_update(request, *args, **kwargs)

        detail_serializer: ArticleDetailCommentsSerializer = ArticleDetailCommentsSerializer(comment)

        return Response(detail_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete Comment",
        request=None,
        responses={
            401: unauthorized_response,
            403: forbidden_response,
            404: "No Comment matches the given query.",
            204: no_content_response
        }
    )
    def destroy(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        comment: Comment = get_object_or_404(Comment, pk=pk)

        user: CustomUser = request.user

        if user != comment.user:
            return Response(data={'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request=request, *args, **kwargs)


class ArticleDetailCommentsView(ListAPIView):
    serializer_class: Type[ArticleDetailCommentsSerializer] = ArticleDetailCommentsSerializer

    def get_queryset(self) -> QuerySet[Comment]:
        article_id: int = self.kwargs.get('pk')
        return Comment.objects.filter(article_id=article_id)

    @extend_schema(
        summary="List Comments",
        request=None,
        responses={
            200: ArticleDetailCommentsSerializer(many=True)
        }
    )
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
    permission_classes: tuple[Type[IsAuthenticated]] = IsAuthenticated,
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        article: Article = Article.objects.filter(pk=pk, status="publish").first()

        if article is not None:
            user: CustomUser = request.user

            favorite: Favorite | None = Favorite.objects.filter(user=user, article=article).first()

            if favorite is None:
                Favorite.objects.create(user=user, article=article)

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
        article: Article = Article.objects.filter(pk=pk, status="publish").first()

        if article is not None:
            user: CustomUser = request.user

            favorite: Favorite | None = Favorite.objects.filter(user=user, article=article).first()

            if favorite is not None:
                favorite.delete()

                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(data={"Maqola foydalanuvchining sevimlilariga qo'shilmagan."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(data={
            "detail": "Maqola topilmadi."
        }, status=status.HTTP_404_NOT_FOUND)


class ClapView(APIView):
    serializer_class: Type[ClapSerializer] = ClapSerializer
    permission_classes: tuple[Type[IsAuthenticated]] = IsAuthenticated,
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        user: CustomUser = request.user

        article: Article = get_object_or_404(self.get_articles_queryset(), pk=pk)

        clap: Clap = Clap.objects.get_or_create(user=user, article=article)[0]

        if clap.count >= 50:
            serializer: ClapSerializer = ClapSerializer(instance=clap, partial=True)

            return Response(data=serializer.data,
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
        user: CustomUser = request.user

        article: Article = get_object_or_404(self.get_articles_queryset(), pk=pk)

        clap: Clap = Clap.objects.filter(article=article, user=user).first()

        if clap is not None:
            clap.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(data={"detail": "Clap Not found."}, status=status.HTTP_404_NOT_FOUND)

    def get_articles_queryset(self) -> QuerySet[Article]:
        return Article.objects.filter(status="publish")


class ReportArticleView(APIView):
    permission_classes: tuple[Type[IsAuthenticated]] = IsAuthenticated,
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,

    def get_queryset(self) -> Response:
        return Article.objects.filter(status="publish")

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        article = get_object_or_404(klass=self.get_queryset(), pk=pk)

        user: CustomUser = request.user

        if Report.objects.filter(article=article, user=user).exists():
            return Response(data=[
                "Ushbu maqola allaqachon shikoyat qilingan."
            ],
                status=status.HTTP_400_BAD_REQUEST)

        Report.objects.create(article=article, user=user)

        if Report.objects.filter(article=article).count() > 3:
            article.status = "trash"
            article.save()

            return Response(data={"detail": "Maqola bir nechta shikoyatlar tufayli olib tashlandi."},
                            status=status.HTTP_200_OK)

        return Response(data={"detail": "Shikoyat yuborildi."},
                        status=status.HTTP_201_CREATED)


class FAQListView(ListAPIView):
    serializer_class: Type[FAQSerializer] = FAQSerializer
    queryset: QuerySet[FAQ] = FAQ.objects.all()
    permission_classes: tuple[Type[AllowAny]] = AllowAny,
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,
