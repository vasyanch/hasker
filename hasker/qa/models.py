from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Tag(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-added_at', '-rating')

    def popular(self):
        return self.order_by('-rating', '-added_at')


class Question(models.Model):
    title = models.CharField(verbose_name='title', max_length=255)
    text = models.TextField()
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    added_at = models.DateTimeField(blank=True, auto_now_add=True)
    rating = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='questions')
    correct_answer = models.OneToOneField('Answer', on_delete=models.SET_NULL, blank=True, null=True,
                                          related_name='correct_answer')
    objects = QuestionManager()

    def __str__(self):
        return self.text

    def get_url(self):
        return reverse('qa:question', args=[self.id])

    def save(self, tags_str=[], *args, **kwargs):
        super(Question, self).save(*args, **kwargs)
        tags = []
        for t in tags_str:
            tag, created = Tag.objects.get_or_create(text=t)
            tags.append(tag)
        self.tags.add(*tags)

    def get_tags(self):
        return self.tags.all()

    def get_answers(self):
        return self.answer_set.all()


class Answer(models.Model):
    text = models.TextField()
    added_at = models.DateTimeField(blank=True, auto_now_add=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(Question, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.text

