# Generated by Django 4.2.14 on 2024-08-27 14:11

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0015_alter_topicfollow_topic_alter_topicfollow_user'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='comment',
            name='content',
            field=ckeditor.fields.RichTextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='articles.comment'),
        ),
        migrations.RemoveField(
            model_name='comment',
            name='text',
        ),
    ]
