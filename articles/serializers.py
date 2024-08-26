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
        fields: list[str] = ["author", "title", "summary", "content", "thumbnail", "topics"]


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Article] = Article
        fields: list[str] = ["id", "author", "title", "summary", "content", "status", "thumbnail", "topics",
                             "created_at", "updated_at", "claps"]

    author: UserSerializer = UserSerializer()
    topics: TopicSerializer = TopicSerializer(many=True)
    claps: ClapSerializer = ClapSerializer(many=True)
