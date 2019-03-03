import os

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import models


def user_directory_path(instance, filename):
    return os.path.join('ava_user_{0}'.format(instance.user.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(verbose_name='profile photo', upload_to=user_directory_path, blank=True, null=True)

    def get_url_avatar(self):
        if self.avatar.name:
            return self.avatar.url
        else:
            return default_storage.url('no_ava.jpg')
