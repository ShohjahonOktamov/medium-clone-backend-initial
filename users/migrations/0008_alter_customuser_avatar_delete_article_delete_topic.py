# Generated by Django 4.2.14 on 2024-08-26 07:47

from django.db import migrations
import django_resized.forms
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_topic_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['top', 'left'], force_format=None, keep_meta=True, null=True, quality=80, scale=1, size=[300, 300], upload_to=users.models.file_upload),
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
    ]
