# Generated by Django 5.1.1 on 2024-10-11 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_assignment_submitted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='attendance_verified',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
