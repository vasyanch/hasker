from django.db import models

from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    return 'ava_user_{0}/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(upload_to=user_directory_path)
