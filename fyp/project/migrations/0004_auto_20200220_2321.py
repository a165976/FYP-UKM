# Generated by Django 2.2.5 on 2020-02-20 15:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0003_auto_20200220_2313'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Datasets',
            new_name='Dataset',
        ),
        migrations.RenameModel(
            old_name='Projects',
            new_name='Project',
        ),
    ]
