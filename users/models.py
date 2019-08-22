import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.urls import reverse

from qa.models import Question, Answer


def user_directory_path(instance, filename):
    return os.path.join('ava_user_{0}'.format(instance.user.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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

    def vote_question(self, question_id, rating, question_title):
        self.id_voted_question = question_id
        self.value_voted_question = rating
        self.title_voted_question = question_title
        self.save()

    def cancel_vote_question(self):
        question = get_object_or_404(Question, id=self.id_voted_question)
        question.cancel_vote(rating=self.value_voted_question)
        self.value_voted_question = self.id_voted_question = self.title_voted_question = None
        self.save()

    def vote_answer(self, answer_id, rating, question_title, question_id):
        self.id_voted_answer = answer_id
        self.value_voted_answer = rating
        self.title_voted_answer = question_title
        self.id_question_voted_answer = question_id
        self.save()

    def cancel_vote_answer(self):
        answer = get_object_or_404(Answer, id=self.id_voted_answer)
        answer.cancel_vote(rating=self.value_voted_answer)
        self.value_voted_answer = self.id_voted_answer = self.title_voted_answer = self.id_question_voted_answer = None
        self.save()

    def get_url_voted_answer(self):
        return reverse('qa:question', args=[self.id_question_voted_answer])

    def get_url_voted_question(self):
        return reverse('qa:question', args=[self.id_voted_question])

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()
