# Generated by Django 4.2.14 on 2024-08-29 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0021_remove_clap_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='clap',
            name='count',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddConstraint(
            model_name='clap',
            constraint=models.UniqueConstraint(fields=('user', 'article'), name='unique_clap'),
        ),
    ]
