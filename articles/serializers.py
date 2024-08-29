from typing import Type

from django.db.models import QuerySet
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Article, Topic, Clap, Comment


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Topic] = Topic
        fields: str = "__all__"


class ClapSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Clap] = Clap
        fields: list[str, str, str] = ['user', 'article', 'count']
        extra_kwargs: dict[str, dict[str, bool]] = {
            'user': {'write_only': True},
            'article': {'write_only': True},
        }


class ArticleCreateSerializer(serializers.ModelSerializer):
    topic_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source="topics",
        queryset=Topic.objects.filter(is_active=True)
    )

    class Meta:
        model: Type[Article] = Article
        fields: tuple[str] = ("title", "summary", "content", "topic_ids")


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Article] = Article
        fields: list[str] = ["id", "author", "title", "summary", "content", "status", "thumbnail", "views_count",
                             "reads_count", "topics",
                             "created_at", "updated_at", "claps_count", "comments_count"]

    author: UserSerializer = UserSerializer()
    topics: TopicSerializer = TopicSerializer(many=True)
    claps_count: serializers.SerializerMethodField = serializers.SerializerMethodField(
        method_name="get_article_claps_count")
    comments_count: serializers.SerializerMethodField = serializers.SerializerMethodField(
        method_name="get_article_comments_count")

    def get_article_claps_count(self, article: Article) -> int:
        return Clap.objects.filter(article=article).count()

    def get_article_comments_count(self, article: Article) -> int:
        return Comment.objects.filter(article=article).count()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Comment] = Comment
        fields: tuple[str] = ('article', 'user', 'content', 'parent')
        extra_kwargs: dict[str, dict[str, bool]] = {
            'article': {'write_only': True},
            'user': {'write_only': True}
        }

    # def validate(self, data: dict[str, int | str]):
    #     article: Article | None = Article.objects.filter(pk=data['article']).first()
    #     if not article or article.status == 'trash':
    #         raise serializers.ValidationError("Cannot add comments to articles that are deleted.")
    #     return data


class ArticleDetailCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Comment] = Comment
        fields: str = ["id", "article", "user", "parent", "content", "created_at", "updated_at", "replies"]

    user: UserSerializer = UserSerializer()
    replies: serializers.SerializerMethodField = serializers.SerializerMethodField(method_name="get_replies")

    def get_replies(self, comment: Comment) -> dict[str, int | list | str]:
        replies: QuerySet[Comment] = comment.replies.all()
        return ArticleDetailCommentsSerializer(instance=replies, many=True).data


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Article] = Article
        fields: list[str] = ["id", "author", "title", "summary", "content", "status", "thumbnail", "views_count",
                             "reads_count", "topics",
                             "created_at", "updated_at", "claps_count", "comments_count"]

    author: UserSerializer = UserSerializer()
    topics: TopicSerializer = TopicSerializer(many=True)
    claps_count: serializers.SerializerMethodField = serializers.SerializerMethodField(
        method_name="get_article_claps_count")
    comments_count: serializers.SerializerMethodField = serializers.SerializerMethodField(
        method_name="get_article_comments_count")

    def get_article_claps_count(self, article: Article) -> int:
        return Clap.objects.filter(article=article).count()

    def get_article_comments_count(self, article: Article) -> int:
        return Comment.objects.filter(article=article).count()
