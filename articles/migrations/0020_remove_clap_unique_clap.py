# Generated by Django 4.2.14 on 2024-08-28 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0019_favorite_alter_clap_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='clap',
            name='unique_clap',
        ),
    ]
