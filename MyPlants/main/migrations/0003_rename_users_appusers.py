# Generated by Django 5.0.1 on 2024-01-21 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_plantlist_users_plants_location_requests_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Users',
            new_name='appUsers',
        ),
    ]
