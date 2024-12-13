# Generated by Django 5.1.1 on 2024-10-12 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_rename_attendance_verified_assignment_assignment_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Syllabus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='syllabus_pdfs/')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.course')),
            ],
        ),
    ]
