import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import HashIndex
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django_resized import ResizedImageField

from users.errors import BIRTH_YEAR_ERROR_MSG


def file_upload(instance, filename):
    """ This function is used to upload the user's avatar. """
    ext = filename.split('.')[-1]
    filename = f'{instance.username}.{ext}'
    return os.path.join('users/avatars/', filename)


class CustomUser(AbstractUser):
    """  This model represents a custom user. """

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

        indexes = [
            HashIndex(fields=['first_name'], name='%(class)s_first_name_hash_idx'),
            HashIndex(fields=['last_name'], name='%(class)s_last_name_hash_idx'),
            HashIndex(fields=['middle_name'], name='%(class)s_middle_name_hash_idx'),
            models.Index(fields=['username'], name='%(class)s_username_idx'),
        ]

        constraints = [
            models.CheckConstraint(
                check=models.Q(birth_year__gt=settings.BIRTH_YEAR_MIN) & models.Q(
                    birth_year__lt=settings.BIRTH_YEAR_MAX),
                name='check_birth_year_range'
            )
        ]

    middle_name = models.CharField(max_length=30, blank=True, null=True)

    avatar = ResizedImageField(size=[300, 300], crop=['top', 'left'], upload_to=file_upload, blank=True, null=True)

    birth_year = models.IntegerField(
        validators=[
            validators.MinValueValidator(settings.BIRTH_YEAR_MIN),
            validators.MaxValueValidator(settings.BIRTH_YEAR_MAX)
        ],
        null=True,
        blank=True
    )

    def clean(self):
        super().clean()
        if self.birth_year and not (settings.BIRTH_YEAR_MIN < self.birth_year < settings.BIRTH_YEAR_MAX):
            raise ValidationError(BIRTH_YEAR_ERROR_MSG)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """ Returns the user's full name. """
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class Recommendation(models.Model):
    class Meta:
        db_table: str = "recommendation"
        verbose_name: str = "Recommendation"
        verbose_name_plural: str = "Recommendations"
        ordering: list[str] = ["-created_at"]

    RECOMMENDATION_TYPE_CHOICES: list[tuple[str, str], tuple[str, str]] = [
        ("more", "More Recommended"),
        ("less", "Less Recommended")
    ]

    topic: models.OneToOneField = models.OneToOneField(to='articles.Topic', on_delete=models.CASCADE)
    recommendation_type: models.CharField = models.CharField(max_length=4, choices=RECOMMENDATION_TYPE_CHOICES)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)


class ReadingHistory(models.Model):
    class Meta:
        db_table: str = "reading_history"
        verbose_name: str = "Reading History"
        verbose_name_plural: str = "Reading Histories"
        ordering: list[str] = ["-created_at"]
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(fields=["user", "article"], name="unique_reading_history")
        ]

    user: models.ForeignKey = models.ForeignKey(to=CustomUser, related_name="reading_history", on_delete=models.CASCADE)
    article: models.ForeignKey = models.ForeignKey(to="articles.Article", related_name="readers",
                                                   on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    class Meta:
        db_table: str = "follow"
        verbose_name: str = "Author Follow"
        verbose_name_plural: str = "Author Follows"
        ordering: list[str] = ["-created_at"]
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(fields=["follower", "followee"], name="unique_author_follow")
        ]

    follower: models.ForeignKey = models.ForeignKey(to=CustomUser, related_name="followings", on_delete=models.CASCADE)
    followee: models.ForeignKey = models.ForeignKey(to=CustomUser, related_name="followers", on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)


class Pin(models.Model):
    class Meta:
        db_table: str = "pin"
        verbose_name: str = "Pin"
        verbose_name_plural: str = "Pins"
        ordering: list[str] = ["-created_at"]

    article: models.OneToOneField = models.OneToOneField(to="articles.Article", related_name="pins",
                                                         on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    class Meta:
        db_table: str = "notification"
        verbose_name: str = "Notification"
        verbose_name_plural: str = "Notifications"
        ordering: list[str] = ["-created_at"]

    user: models.ForeignKey = models.ForeignKey(to=CustomUser, related_name="notifications", on_delete=models.CASCADE)
    read: models.BooleanField = models.BooleanField(default=False)
    read_at: models.DateTimeField = models.DateTimeField(null=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
