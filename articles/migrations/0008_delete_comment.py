# Generated by Django 4.2.14 on 2024-08-26 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_clap_created_at_clap_updated_at_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
