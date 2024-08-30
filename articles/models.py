from ckeditor.fields import RichTextField
from django.conf import settings
from django.db.models import Model, CharField, TextField, BooleanField, ForeignKey, ImageField, ManyToManyField, \
    DateTimeField, PositiveBigIntegerField, CASCADE, UniqueConstraint, PositiveSmallIntegerField

from users.models import CustomUser


class Topic(Model):
    class Meta:
        db_table: str = "topic"
        verbose_name: str = 'Topic'
        verbose_name_plural: str = "Topics"
        ordering: list[str] = ["name"]

    name: CharField = CharField(max_length=50)
    description: TextField = TextField()
    is_active: BooleanField = BooleanField(default=True)

    def __str__(self) -> CharField:
        return self.name


class Article(Model):
    STATUS_CHOICES: list[tuple[str, str]] = [
        ("pending", "Pending"),
        ("publish", "Publish"),
        ("trash", "Deleted"),
        ("archive", "Archived")
    ]

    class Meta:
        db_table: str = "article"
        verbose_name: str = 'Article'
        verbose_name_plural: str = "Articles"
        ordering: list[str] = ["-created_at"]

    author: ForeignKey = ForeignKey(to=CustomUser, on_delete=CASCADE)
    title: CharField = CharField(max_length=100)
    summary: CharField = CharField(max_length=200)
    content: RichTextField = RichTextField()
    status: CharField = CharField(choices=STATUS_CHOICES, default="pending", max_length=7)
    thumbnail: ImageField = ImageField(upload_to="thumbnails/", blank=True, null=True)
    topics: ManyToManyField = ManyToManyField(to=Topic)
    views_count: PositiveBigIntegerField = PositiveBigIntegerField(default=0)
    reads_count: PositiveBigIntegerField = PositiveBigIntegerField(default=0)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now_add=True)

    def __str__(self) -> CharField:
        return self.title


class Clap(Model):
    class Meta:
        db_table: str = "clap"
        verbose_name: str = 'Clap'
        verbose_name_plural: str = 'Claps'
        constraints: list[UniqueConstraint] = [
            UniqueConstraint(fields=["user", "article"], name="unique_clap")
        ]

    article: ForeignKey = ForeignKey(to=Article, on_delete=CASCADE, related_name="claps")
    user: ForeignKey = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    count: PositiveSmallIntegerField = PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username} clapped {self.article.name}"


class Comment(Model):
    class Meta:
        db_table: str = "comment"
        verbose_name: str = 'Comment'
        verbose_name_plural: str = 'Comments'
        ordering: list[str] = ["-created_at"]

    article: ForeignKey = ForeignKey(to=Article, on_delete=CASCADE, related_name="comments")
    user: ForeignKey = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    content: RichTextField = RichTextField()
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now_add=True)
    parent: ForeignKey = ForeignKey(to='self', null=True, on_delete=CASCADE, related_name='replies')

    def __str__(self) -> str:
        return f"{self.user.username} commented {self.article.name}"


class TopicFollow(Model):
    class Meta:
        db_table: str = "topic_follow"
        verbose_name: str = 'Topic Follow'
        verbose_name_plural: str = 'Topic Follows'
        ordering: list[str] = ["-created_at"]
        constraints: list[UniqueConstraint] = [
            UniqueConstraint(fields=["user", "topic"], name="unique_topic_follow")
        ]

    user: ForeignKey = ForeignKey(to='users.CustomUser', on_delete=CASCADE, related_name="following")
    topic: ForeignKey = ForeignKey(to=Topic, on_delete=CASCADE, related_name="followers")
    created_at: DateTimeField = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} followed {self.topic.name}"


class Favorite(Model):
    class Meta:
        db_table: str = "favorite"
        verbose_name: str = 'Favorite'
        verbose_name_plural: str = 'Favorites'
        ordering: list[str] = ["-created_at"]
        constraints: list[UniqueConstraint] = [
            UniqueConstraint(fields=["user", "article"], name="unique_favorite")
        ]

    user: ForeignKey = ForeignKey(to="users.CustomUser", related_name="favorites", on_delete=CASCADE)
    article: ForeignKey = ForeignKey(to=Article, related_name="favorited_by", on_delete=CASCADE)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} favorited {self.article.name}"


class Report(Model):
    class Meta:
        db_table: str = "report"
        verbose_name: str = 'Report'
        verbose_name_plural: str = 'Reports'
        ordering: list[str] = ["-created_at"]
        constraints: list[UniqueConstraint] = [
            UniqueConstraint(fields=["user", "article"], name="unique_report")
        ]

    user: ForeignKey = ForeignKey(to="users.CustomUser", related_name="reports", on_delete=CASCADE)
    article: ForeignKey = ForeignKey(to=Article, related_name="reported_by", on_delete=CASCADE)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)


class FAQ(Model):
    class Meta:
        db_table: str = "faq"
        verbose_name: str = 'FAQ'
        verbose_name_plural: str = 'FAQs'
        ordering: list[str] = ["-created_at"]

    question: TextField = TextField(null=True, blank=True)
    answer: RichTextField = RichTextField(null=True, blank=True)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
