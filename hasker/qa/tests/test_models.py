import datetime
from django.test import TestCase
from django.utils import timezone

from qa.models import Question, Tag, Answer
from users.models import User, UserProfile


class QuestionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create()
        UserProfile.objects.create(user=self.user)
        self.q_first = Question.objects.create(title='first', author=self.user)
        self.q_first.save(['first', 'two', 'three'])
        self.q_no_tags = Question.objects.create(title='no_tags', author=self.user)
        Answer.objects.create(
            question=self.q_first,
            author=self.user
        )
        Answer.objects.create(
            question=self.q_first,
            rating=10,
            author=self.user
        )
        Answer.objects.create(
            question=self.q_first,
            added_at=timezone.now() - datetime.timedelta(days=1),
            author=self.user
        )
        Answer.objects.create(
            question=self.q_first,
            added_at=timezone.now() - datetime.timedelta(days=1),
            rating=10,
            author=self.user
        )

    def test_def_rating(self):
        self.assertEqual(self.q_first.rating, 0)

    def test_get_url(self):
        self.assertEqual('/qa/question/1/', self.q_first.get_url())

    def test_get_tags(self):
        tags = Tag.objects.filter(questions=self.q_first.id)
        self.assertQuerysetEqual(self.q_first.get_tags(), map(repr, tags), ordered=False)

    def test_empty_get_tags(self):
        tags = Tag.objects.filter(questions=self.q_no_tags.id)
        self.assertQuerysetEqual(self.q_no_tags.get_tags(), tags)

    def test_get_answers(self):
        answers = Answer.objects.filter(question__id=self.q_first.id).order_by('-rating', 'added_at')
        self.assertQuerysetEqual(self.q_first.get_answers(), map(repr, answers))

    def test_get_date(self):
        today = timezone.now().strftime("%d.%m.%Y")
        self.assertEqual(self.q_first.get_date(), today)

    def test_vote(self):
        self.q_first.vote(1, self.user)
        self.assertEqual(self.q_first.rating, 1)
        self.q_first.vote(-1, self.user)
        self.assertEqual(self.q_first.rating, 0)
        list_values = ['1', [1], 10, 0, 2, {}, ('t',)]
        for i in list_values:
            self.q_first.vote(i, self.user)
            self.assertEqual(self.q_first.rating, 0)


class AnswerModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create()
        UserProfile.objects.create(user=self.user)
        self.question = Question.objects.create(title='for_answer', author=self.user)
        self.answer_no_correct = Answer.objects.create(text='no correct', question=self.question, author=self.user)
        self.answer_correct = Answer.objects.create(text='correct', question=self.question, author=self.user)
        self.question.correct_answer = self.answer_correct

    def test_get_date(self):
        today = timezone.now().strftime("%d.%m.%Y")
        self.assertEqual(self.answer_correct.get_date(), today)

    def test_is_correct(self):
        self.assertIs(self.answer_no_correct.is_correct(), False)
        self.assertIs(self.answer_correct.is_correct(), True)

    def test_vote(self):
        self.answer_correct.vote(1, self.user)
        self.assertEqual(self.answer_correct.rating, 1)
        self.answer_correct.vote(-1, self.user)
        self.assertEqual(self.answer_correct.rating, 0)
        list_values = ['1', [1], 10, 0, 2, {}, ('t',)]
        for i in list_values:
            self.answer_correct.vote(i, self.user)
            self.assertEqual(self.answer_correct.rating, 0)
