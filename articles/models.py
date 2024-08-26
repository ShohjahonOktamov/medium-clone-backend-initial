from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, TextField, BooleanField, ForeignKey, ImageField, ManyToManyField, \
    DateTimeField, CASCADE
from django.utils import timezone

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
        ("publish", "Publish")
    ]

    class Meta:
        db_table: str = "article"
        verbose_name: str = 'Article'
        verbose_name_plural: str = "Articles"
        ordering: list[str] = ["-created_at"]

    author: ForeignKey = ForeignKey(to=CustomUser, on_delete=CASCADE)
    title: CharField = CharField(max_length=100)
    summary: CharField = CharField(max_length=200)
    content: TextField = TextField()
    status: CharField = CharField(choices=STATUS_CHOICES, default="pending")
    thumbnail: ImageField = ImageField(upload_to="thumbnails/")
    topic_ids: ManyToManyField = ManyToManyField(to=Topic, blank=True)
    created_at: DateTimeField = DateTimeField(default=timezone.now)
    updated_at: DateTimeField = DateTimeField(default=timezone.now)

    def __str__(self) -> CharField:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if self.topic_ids.count() > 5:
            raise ValidationError("An article can only have up to 5 topics.")
        super().save(*args, **kwargs)


class Clap(Model):
    class Meta:
        db_table: str = "clap"
        verbose_name: str = 'Clap'
        verbose_name_plural: str = 'Claps'
        unique_together: tuple[str, str] = ("article", "user")

    article: ForeignKey = ForeignKey(to=Article, on_delete=CASCADE, related_name="claps")
    user: ForeignKey = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
