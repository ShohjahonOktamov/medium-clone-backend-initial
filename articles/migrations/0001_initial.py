# Generated by Django 4.2.14 on 2024-08-26 08:23

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('summary', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('publish', 'Publish')], default='pending')),
                ('thumbnail', models.ImageField(upload_to='thumbnails/')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'db_table': 'article',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
                'db_table': 'topic',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Clap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claps', to='articles.article')),
            ],
            options={
                'verbose_name': 'Clap',
                'verbose_name_plural': 'Claps',
                'db_table': 'clap',
            },
        ),
    ]
