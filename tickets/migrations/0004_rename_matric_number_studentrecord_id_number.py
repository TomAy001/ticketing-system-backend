# Generated by Django 4.2.7 on 2025-07-15 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_rename_department_studentrecord_programme_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentrecord',
            old_name='matric_number',
            new_name='id_number',
        ),
    ]
