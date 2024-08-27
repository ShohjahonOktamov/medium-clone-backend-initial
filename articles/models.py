from ckeditor.fields import RichTextField
from django.conf import settings
from django.db.models import Model, CharField, TextField, BooleanField, ForeignKey, ImageField, ManyToManyField, \
    DateTimeField, PositiveBigIntegerField, CASCADE

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
    STATUS_CHOICES: list[tuple[str, str], tuple[str, str], tuple[str, str]] = [
        ("pending", "Pending"),
        ("publish", "Publish"),
        ("trash", "Deleted")
    ]

    class Meta:
        db_table: str = "article"
        verbose_name: str = 'Article'
        verbose_name_plural: str = "Articles"
        ordering: list[str] = ["-created_at"]

    author: ForeignKey = ForeignKey(to=CustomUser, on_delete=CASCADE, null=True, blank=True)
    title: CharField = CharField(max_length=100)
    summary: CharField = CharField(max_length=200)
    content: RichTextField = RichTextField()
    status: CharField = CharField(choices=STATUS_CHOICES, default="pending", max_length=7)
    thumbnail: ImageField = ImageField(upload_to="thumbnails/", blank=True, null=True)
    topics: ManyToManyField = ManyToManyField(to=Topic, blank=True)
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
        unique_together: tuple[str, str] = ("article", "user")

    article: ForeignKey = ForeignKey(to=Article, on_delete=CASCADE, related_name="claps")
    user: ForeignKey = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now_add=True)


class Comment(Model):
    class Meta:
        db_table: str = "comment"
        verbose_name: str = 'Comment'
        verbose_name_plural: str = 'Comments'
        ordering: list[str] = ["-created_at"]
        unique_together: tuple[str, str] = ("article", "user")

    article: ForeignKey = ForeignKey(to=Article, on_delete=CASCADE, related_name="comments")
    user: ForeignKey = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    text: TextField = TextField()
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now_add=True)


class TopicFollow(Model):
    class Meta:
        db_table: str = "follow"
        verbose_name: str = 'Follow'
        verbose_name_plural: str = 'Follows'
        ordering: list[str] = ["-created_at"]
        unique_together: tuple[str, str] = ("user", "topic")

    user: ForeignKey = ForeignKey(to='users.CustomUser', on_delete=CASCADE, related_name="following")
    topic: ForeignKey = ForeignKey(to=Topic, on_delete=CASCADE, related_name="followers")
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
