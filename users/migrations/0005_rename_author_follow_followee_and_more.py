# Generated by Django 4.2.14 on 2024-08-29 19:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_follow'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='author',
            new_name='followee',
        ),
        migrations.RenameField(
            model_name='follow',
            old_name='user',
            new_name='follower',
        ),
    ]
