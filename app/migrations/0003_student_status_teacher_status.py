# Generated by Django 5.1.1 on 2024-09-27 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
        migrations.AddField(
            model_name='teacher',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]
