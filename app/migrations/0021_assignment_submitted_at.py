# Generated by Django 5.1.1 on 2024-10-04 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_assignment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
