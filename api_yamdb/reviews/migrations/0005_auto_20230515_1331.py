# Generated by Django 3.2 on 2023-05-15 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20230514_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='confirmation_code',
            field=models.SlugField(blank=True, editable=False, max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.SlugField(choices=[('user', 'user'), ('admin', 'admin'), ('moderator', 'moderator')], default='user', max_length=10),
        ),
    ]
