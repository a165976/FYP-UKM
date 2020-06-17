# Generated by Django 3.0.3 on 2020-05-01 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20200309_2255'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('columns', models.TextField()),
                ('size', models.CharField(max_length=100)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='project.Project')),
            ],
        ),
    ]
