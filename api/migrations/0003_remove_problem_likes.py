# Generated by Django 4.2.7 on 2024-09-26 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_customuser_comment_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='likes',
        ),
    ]
