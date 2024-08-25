# Generated by Django 4.2.14 on 2024-08-25 15:17

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_customuser_check_birth_year_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='first_name_en',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='first_name_ru',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='first_name_uz',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name_en',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='last name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name_ru',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='last name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name_uz',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='last name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='middle_name_en',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='middle_name_ru',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='middle_name_uz',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=django.contrib.postgres.indexes.HashIndex(fields=['first_name'], name='customuser_first_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=django.contrib.postgres.indexes.HashIndex(fields=['last_name'], name='customuser_last_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=django.contrib.postgres.indexes.HashIndex(fields=['middle_name'], name='customuser_middle_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['username'], name='customuser_username_idx'),
        ),
    ]
