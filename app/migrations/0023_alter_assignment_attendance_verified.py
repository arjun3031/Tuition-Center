# Generated by Django 5.1.1 on 2024-10-11 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_assignment_attendance_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='attendance_verified',
            field=models.CharField(default='Not Verified', max_length=20),
        ),
    ]
