import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse

from qa.models import Question, Answer


def user_directory_path(instance, filename):
    return os.path.join('ava_user_{0}'.format(instance.user.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(verbose_name='profile photo', upload_to=user_directory_path, blank=True, null=True)
    value_voted_question = models.IntegerField(default=None, null=True)
    id_voted_question = models.IntegerField(default=None, null=True)
    title_voted_question = models.CharField(default=None, null=True, max_length=255)
    value_voted_answer = models.IntegerField(default=None, null=True)
    id_voted_answer = models.IntegerField(default=None, null=True)
    title_voted_answer = models.CharField(default=None, null=True, max_length=255)
    id_question_voted_answer = models.IntegerField(default=None, null=True)

    def get_url_avatar(self):
        if self.avatar.name:
            return self.avatar.url
        return os.path.join(settings.STATIC_URL, 'users/images/no_ava.jpg')

    def get_date_joined(self):
        return self.user.date_joined.strftime("%d.%m.%Y")

    def get_url(self):
        return reverse('users:profile', args=[self.user_id])

    def get_url_voted_answer(self):
        return reverse('qa:question', args=[self.id_question_voted_answer])

    def get_url_voted_question(self):
        return reverse('qa:question', args=[self.id_voted_question])

    def cancel_vote_question(self):
        question = get_object_or_404(Question, id=self.id_voted_question)
        question.rating = question.rating - self.value_voted_question
        question.save()
        self.value_voted_question = self.id_voted_question = self.title_voted_question = None

    def cancel_vote_answer(self):
        answer = get_object_or_404(Answer, id=self.id_voted_answer)
        answer.rating = answer.rating - self.value_voted_answer
        answer.save()
        self.value_voted_answer = self.id_voted_answer = self.title_voted_answer = self.id_question_voted_answer = None
