# Generated by Django 5.0.1 on 2024-02-08 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_rename_todolist_item_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='list',
            name='user',
        ),
        migrations.DeleteModel(
            name='Item',
        ),
        migrations.DeleteModel(
            name='List',
        ),
    ]
