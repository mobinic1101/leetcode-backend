# Generated by Django 5.1.1 on 2025-01-04 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_problem_allowed_imports'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='allowed_imports',
            field=models.CharField(blank=True, help_text='comma-separated list of allowed imports', max_length=200, null=True),
        ),
    ]
