import datetime

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from qa.models import Question, Answer
from qa.forms import AskForm, AnswerForm
from users.models import User, UserProfile


class IndexViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='vasya')
        Question.objects.create(
            title='first',
            author=user,
            text='today_0'
        )
        Question.objects.create(
            title='second',
            author=user,
            text='today_10',
            rating=10,
            )
        Question.objects.create(
            title='third',
            author=user,
            text='yesterday_0',
            added_at=timezone.now() - datetime.timedelta(days=1)
        )
        Question.objects.create(
            title='fourth',
            author=user,
            text='yesterday_10',
            added_at=timezone.now() - datetime.timedelta(days=1),
            rating=10
        )

    def check_trending(self, response):
        trending_list_questions = Question.objects.popular()
        self.assertQuerysetEqual(response.context['trending'], map(repr, trending_list_questions))

    def test_IndexView_new(self):
        response = self.client.get(reverse('index'))
        right_list_questions = Question.objects.all().order_by('-added_at', '-rating')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual([i.name for i in response.templates],
                             ['qa/index.html', 'qa/list_questions.html', 'base.html'])
        self.assertQuerysetEqual(response.context['list_questions'], map(repr, right_list_questions))
        self.check_trending(response)

    def test_IndexView_pop(self):
        response = self.client.get(reverse('qa:index_pop'))
        right_list_questions = Question.objects.all().order_by('-rating', '-added_at')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual([i.name for i in response.templates],
                             ['qa/index.html', 'qa/list_questions.html', 'base.html'])
        self.assertQuerysetEqual(response.context['list_questions'], map(repr, right_list_questions))
        self.check_trending(response)


class QuestionAddViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='vasya')
        testuser = User.objects.create(username='testuser')
        testuser.set_password('testuser123')
        testuser.save()
        UserProfile.objects.create(user=testuser)
        Question.objects.create(
            title='first',
            author=user,
            text='today_0'
        )
        Question.objects.create(
            title='second',
            author=user,
            text='today_10',
            rating=10,
        )
        Question.objects.create(
            title='third',
            author=user,
            text='yesterday_0',
            added_at=timezone.now() - datetime.timedelta(days=1)
        )
        Question.objects.create(
            title='fourth',
            author=user,
            text='yesterday_10',
            added_at=timezone.now() - datetime.timedelta(days=1),
            rating=10
        )

    def check_trending(self, response):
        trending_list_questions = Question.objects.popular()
        self.assertQuerysetEqual(response.context['trending'], map(repr, trending_list_questions))

    def test_QuestionAddView_get(self):
        self.client.login(username='testuser', password='testuser123')
        user = User.objects.get(username='testuser')
        response = self.client.get(reverse('qa:ask'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_add.html', [i.name for i in response.templates])
        self.assertEqual(response.context['form']._user, user)
        self.assertIsInstance(response.context['form'], AskForm)
        self.check_trending(response)
        self.client.logout()

    def test_QuestionAddView_post_bad(self):
        self.client.login(username='testuser', password='testuser123')
        user = User.objects.get(username='testuser')
        response = self.client.post(reverse('qa:ask'),
                                    data={'title': 'a'*101, 'text': 'test question', 'tags': 'django, test, vasya'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_add.html', [i.name for i in response.templates])
        self.assertEqual(response.context['form']._user, user)
        self.assertIsInstance(response.context['form'], AskForm)
        self.assertIs(response.context['form'].is_valid(), False)
        self.check_trending(response)
        self.client.logout()

    def test_QuestionAddView_post_ok(self):
        self.client.login(username='testuser', password='testuser123')
        response = self.client.post(reverse('qa:ask'),
                                    data={'title': 'new_question', 'text': 'new question', 'tags': 'django,test,vasya'},
                                    follow=True)
        new_question = Question.objects.get(title='new_question')
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_details.html', [i.name for i in response.templates])
        self.assertEqual(response.redirect_chain, [(reverse('qa:question', args=[new_question.id]), 302)])
        self.assertRedirects(response, reverse('qa:question', args=[new_question.id]))
        self.assertQuerysetEqual(new_question.get_tags(),
                                 ['<Tag: django>', '<Tag: test>', '<Tag: vasya>'],
                                 ordered=False)
        self.assertEqual(new_question.text, 'new question')
        self.client.logout()


class QuestionDetalsViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='vasya')
        testuser = User.objects.create(username='testuser')
        testuser.set_password('testuser123')
        testuser.save()
        UserProfile.objects.create(user=testuser)
        question = Question.objects.create(
            title='first',
            author=user,
            text='today_0'
        )
        Question.objects.create(
            title='second',
            author=user,
            text='today_10',
            rating=10,
        )
        Question.objects.create(
            title='third',
            author=user,
            text='yesterday_0',
            added_at=timezone.now() - datetime.timedelta(days=1)
        )
        Question.objects.create(
            title='fourth',
            author=user,
            text='yesterday_10',
            added_at=timezone.now() - datetime.timedelta(days=1),
            rating=10
        )
        answer = Answer.objects.create(
            text='answer today_0',
            author=testuser,
            question=question
        )
        self.id_testquestion = question.id
        self.id_testanswer = answer.id

    def check_trending(self, response):
        trending_list_questions = Question.objects.popular()
        self.assertQuerysetEqual(response.context['trending'], map(repr, trending_list_questions))

    def test_QuestionDetailsView_get_AnonymousUser(self):
        question = Question.objects.get(id=self.id_testquestion)
        response = self.client.get(reverse('qa:question', args=[self.id_testquestion]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_details.html', [i.name for i in response.templates])
        self.assertListEqual([i.name for i in response.templates],
                             ['qa/question_details.html', 'base.html'])
        self.assertListEqual([i.name for i in response.templates], ['qa/question_details.html', 'base.html'])
        self.assertEqual(response.context['question'], question)
        self.assertIsInstance(response.context['user'], AnonymousUser)
        self.assertIsNone(response.context.get('form'))
        self.check_trending(response)
        self.client.logout()

    def test_QuestionDetailsView_get_testuser(self):
        self.client.login(username='testuser', password='testuser123')
        question = Question.objects.get(id=self.id_testquestion)
        testuser = User.objects.get(username='testuser')
        response = self.client.get(reverse('qa:question', args=[self.id_testquestion]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_details.html', [i.name for i in response.templates])
        self.assertEqual(response.context['question'], question)
        self.assertEqual(response.context['user'], testuser)
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEqual(response.context['form']._user, testuser)
        self.check_trending(response)
        self.client.logout()

    def test_QuestionDetailsView_post_vote_question(self):
        self.client.login(username='testuser', password='testuser123')
        testuser = User.objects.get(username='testuser')
        question = Question.objects.get(id=self.id_testquestion)
        self.assertEqual(question.rating, 0)
        response = self.client.post(reverse('qa:question', args=[self.id_testquestion]),
                                    data={'rating': '+1', 'models': 'question', 'object_id': self.id_testquestion})
        question = Question.objects.get(id=self.id_testquestion)
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_details.html', [i.name for i in response.templates])
        self.assertEqual(question.rating, 1)
        self.assertEqual(response.context['vote_error'], '')
        self.assertEqual(response.context['user'], testuser)
        self.assertEqual(response.context['question'], question)
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEqual(response.context['form']._user, testuser)
        self.check_trending(response)
        response = self.client.post(reverse('qa:question', args=[self.id_testquestion]),
                                    data={'rating': '+1', 'models': 'question', 'object_id': self.id_testquestion})
        self.assertEqual(response.context['vote_error'], 'Sorry, you can vote only one question and one answer! '
                                                         'But you can change you choice! See you profile page.')
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEqual(response.context['form']._user, testuser)
        self.check_trending(response)
        self.client.logout()

    def test_QuestionDetailsView_post_vote_answer(self):
        self.client.login(username='testuser', password='testuser123')
        testuser = User.objects.get(username='testuser')
        question = Question.objects.get(id=self.id_testquestion)
        answer = Answer.objects.get(id=self.id_testanswer)
        self.assertEqual(answer.rating, 0)
        response = self.client.post(reverse('qa:question', args=[self.id_testquestion]),
                                    data={'rating': '-1', 'models': 'answer', 'object_id': self.id_testanswer})
        answer = Answer.objects.get(id=self.id_testanswer)
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_details.html', [i.name for i in response.templates])
        self.assertEqual(answer.rating, -1)
        self.assertEqual(response.context['vote_error'], '')
        self.assertEqual(response.context['user'], testuser)
        self.assertEqual(response.context['question'], question)
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEqual(response.context['form']._user, testuser)
        self.check_trending(response)
        response = self.client.post(reverse('qa:question', args=[self.id_testquestion]),
                                    data={'rating': '+1', 'models': 'answer', 'object_id': self.id_testanswer})
        self.assertEqual(response.context['vote_error'], 'Sorry, you can vote only one question and one answer! '
                                                         'But you can change you choice! See you profile page.')
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEqual(response.context['form']._user, testuser)
        self.check_trending(response)
        self.client.logout()

    def test_QuestionDetailsView_post_correct_answer(self):
        self.client.login(username='testuser', password='testuser123')
        testuser = User.objects.get(username='testuser')
        correct_answer = Answer.objects.get(id=self.id_testanswer)
        response = self.client.post(reverse('qa:question', args=[self.id_testquestion]),
                                    data={'correct_answer': '{}'.format(self.id_testanswer)})
        question = Question.objects.get(id=self.id_testquestion)
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_details.html', [i.name for i in response.templates])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['question'], question)
        self.assertEqual(response.context['user'], testuser)
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEqual(response.context['form']._user, testuser)
        self.assertEqual(question.correct_answer, correct_answer)
        self.assertIsInstance(response.context['form'], AnswerForm)
        self.assertEqual(response.context['form']._user, testuser)
        self.check_trending(response)
        self.client.logout()

    def test_QuestionDetailsView_post_add_answer(self):
        self.client.login(username='testuser', password='testuser123')
        testuser = User.objects.get(username='testuser')
        question = Question.objects.get(id=self.id_testquestion)
        response = self.client.post(reverse('qa:question', args=[self.id_testquestion]),
                                    data={'text': 'answer from testuser', 'question': '%s' % self.id_testquestion},
                                    follow=True)
        new_answer = Answer.objects.get(text='answer from testuser')
        self.assertEqual(response.status_code, 200)
        self.assertIn('base.html', [i.name for i in response.templates])
        self.assertIn('qa/question_details.html', [i.name for i in response.templates])
        self.assertIn(new_answer, question.get_answers())
        self.assertEqual(response.redirect_chain, [(reverse('qa:question', args=[self.id_testquestion]), 302)])
        self.assertEqual(response.context['user'], testuser)
        self.client.logout()


class SearchView(TestCase):
    def setUp(self):
        user = User.objects.create(username='vasya')
        question = Question.objects.create(
            title='first',
            author=user,
            text='today_0'
        )
        question.save(['test', 'django'])
        Question.objects.create(
            title='second',
            author=user,
            text='today_10',
            rating=10,
        )
        Question.objects.create(
            title='third',
            author=user,
            text='yesterday_0',
            added_at=timezone.now() - datetime.timedelta(days=1)
        )
        Question.objects.create(
            title='fourth',
            author=user,
            text='yesterday_10',
            added_at=timezone.now() - datetime.timedelta(days=1),
            rating=10
        )

    def check_trending(self, response):
        trending_list_questions = Question.objects.popular()
        self.assertQuerysetEqual(response.context['trending'], map(repr, trending_list_questions))

    def test_SearchView(self):
        response = self.client.get(reverse('qa:search'), data={'query': 'today'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_questions']), 2)
        self.assertListEqual([i.name for i in response.templates],
                             ['qa/search_result.html', 'qa/list_questions.html', 'base.html'])
        self.check_trending(response)
        response = self.client.get(reverse('qa:search'), data={'query': 'fourth'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_questions']), 1)
        self.assertListEqual([i.name for i in response.templates],
                             ['qa/search_result.html', 'qa/list_questions.html', 'base.html'])
        self.check_trending(response)

    def test_SearchTagView(self):
        response = self.client.get(reverse('qa:search_tag', args=['test']))
        questions = Question.objects.filter(title='first')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['list_questions'], map(repr, questions))
        self.assertListEqual([i.name for i in response.templates],
                             ['qa/tag_search_result.html', 'qa/list_questions.html', 'base.html'])
        self.assertEqual(len(response.context['list_questions']), 1)
        self.check_trending(response)
        response = self.client.get(reverse('qa:search'), data={'query': 'tag:django'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_questions']), 1)
        self.assertQuerysetEqual(response.context['list_questions'], map(repr, Question.objects.filter(title='first')))
        self.assertListEqual([i.name for i in response.templates],
                             ['qa/tag_search_result.html', 'qa/list_questions.html', 'base.html'])
        self.check_trending(response)
