# Generated by Django 4.2.14 on 2024-08-26 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0009_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='reads_count',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='article',
            name='views_count',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
