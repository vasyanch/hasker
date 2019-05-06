# Generated by Django 2.1 on 2019-05-05 19:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=users.models.user_directory_path, verbose_name='profile photo')),
                ('value_voted_question', models.IntegerField(default=None, null=True)),
                ('id_voted_question', models.IntegerField(default=None, null=True)),
                ('title_voted_question', models.CharField(default=None, max_length=255, null=True)),
                ('value_voted_answer', models.IntegerField(default=None, null=True)),
                ('id_voted_answer', models.IntegerField(default=None, null=True)),
                ('title_voted_answer', models.CharField(default=None, max_length=255, null=True)),
                ('id_question_voted_answer', models.IntegerField(default=None, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
