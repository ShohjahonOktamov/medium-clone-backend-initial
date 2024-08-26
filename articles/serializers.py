from typing import Type

from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Article, Topic, Clap


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Topic] = Topic
        fields: str = "__all__"


class ClapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clap
        fields = ['user']

    user = UserSerializer()


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Article] = Article
        fields: list[str] = ["title", "summary", "content", "thumbnail", "topic_ids"]

    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.filter(is_active=True),
        many=True,
        required=False
    )


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Article] = Article
        fields: list[str] = ["id", "author", "title", "summary", "content", "status", "thumbnail", "topic_ids",
                             "created_at", "updated_at", "claps"]

    author: UserSerializer = UserSerializer()
    topic_ids: TopicSerializer = TopicSerializer(many=True)
    claps: ClapSerializer = ClapSerializer(many=True)
