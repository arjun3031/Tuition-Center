# Generated by Django 5.1.1 on 2024-10-03 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_delete_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='pdf_file',
            field=models.FileField(null=True, upload_to='assignments/'),
        ),
    ]
