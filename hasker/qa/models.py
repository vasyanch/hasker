from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Tag(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Vote:
    def vote(self, rating):
        if rating in (-1, 1):
            self.rating += rating
            self.save()
            return True
        return False


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-added_at', '-rating')

    def popular(self):
        return self.order_by('-rating', '-added_at')


class Question(Vote, models.Model):
    title = models.CharField(verbose_name='title', max_length=255)
    text = models.TextField()
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
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
        tags_list = []
        for t in tags_str:
            tag, created = Tag.objects.get_or_create(text=t)
            tags_list.append(tag)
        self.tags.add(*tags_list)

    def get_tags(self):
        return self.tags.all()

    def get_answers(self):
        return self.answer_set.order_by('-rating', 'added_at')

    def get_date(self):
        return self.added_at.strftime("%d.%m.%Y")

    def vote(self, rating, user):
        if super(Question, self).vote(rating):
            user.userprofile.vote_question(question_id=self.id,
                                           rating=rating,
                                           question_title=self.title)

    def cancel_vote(self, rating):
        self.rating = self.rating - rating
        self.save()


class Answer(Vote, models.Model):
    text = models.TextField()
    added_at = models.DateTimeField(blank=True, auto_now_add=True)
    rating = models.IntegerField(default=0)
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def get_date(self):
        return self.added_at.strftime("%d.%m.%Y")

    def is_correct(self):
        if self.question.correct_answer_id == self.id:
            return True
        return False

    def vote(self, rating, user):
        if super(Answer, self).vote(rating):
            user.userprofile.vote_answer(answer_id=self.id,
                                         rating=rating,
                                         question_title=self.question.title,
                                         question_id=self.question.id)

    def cancel_vote(self, rating):
        self.rating = self.rating - rating
        self.save()

