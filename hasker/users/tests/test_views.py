import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from qa.models import Question, Answer
from users.forms import SignupForm, UserProfileSignupForm, ChangeFieldsForm
from users.models import User, UserProfile


class SignUpViewTest(TestCase):
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

    def check_templates(self, response, list_temp):
        templates = [i.name for i in response.templates]
        for i in list_temp:
            self.assertIn(i, templates)

    def test_get(self):
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], SignupForm)
        self.assertIsInstance(response.context['profile_form'], UserProfileSignupForm)
        self.check_templates(response, ['users/signup.html', 'base.html'])
        self.check_trending(response)

    def test_post_bad(self):
        response = self.client.post(reverse('users:signup'),
                                    data={'username': 'vasya', 'password1': 'vasya123', 'password2': 'asdf123'})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], SignupForm)
        self.assertIsInstance(response.context['profile_form'], UserProfileSignupForm)
        self.check_templates(response, ['users/signup.html', 'base.html'])
        self.check_trending(response)

    def test_post_ok(self):
        response = self.client.post(reverse('users:signup'),
                                    data={'username': 'django', 'password1': 'django123TEST',
                                          'password2': 'django123TEST', 'email': 'django@mail.ru'},
                                    follow=True)
        new_user = User.objects.get(username='django')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_user.email, 'django@mail.ru')
        self.assertEqual(response.redirect_chain, [(reverse('index'), 302)])
        self.assertIsInstance(new_user.userprofile, UserProfile)
        self.check_templates(response, ['qa/index.html', 'qa/list_questions.html', 'base.html'])
        self.check_trending(response)


class LogInViewTest(TestCase):
    def setUp(self):
        testuser = User.objects.create(username='testuser')
        testuser.set_password('testuser123')
        testuser.save()
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

    def check_templates(self, response, list_temp):
        templates = [i.name for i in response.templates]
        for i in list_temp:
            self.assertIn(i, templates)

    def test_get(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.check_templates(response, ['base.html', 'users/login.html'])
        self.check_trending(response)

    def test_post_bad(self):
        response = self.client.post(reverse('users:login'), data={'username': 'user', 'password': 'user'})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.assertEqual(response.context['error'], 'Invalid username/password')
        self.check_templates(response, ['base.html', 'users/login.html'])
        self.check_trending(response)

    def test_post_ok(self):
        response = self.client.post(reverse('users:login'),
                                    data={'username': 'testuser', 'password': 'testuser123'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse('index'), 302)])
        self.check_templates(response, ['qa/index.html', 'qa/list_questions.html', 'base.html'])
        self.check_trending(response)


class ProfileViewTest(TestCase):
    def setUp(self):
        testuser = User.objects.create(username='testuser')
        testuser.set_password('testuser123')
        testuser.save()
        UserProfile.objects.create(user=testuser)
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
        question = Question.objects.create(
            title='fourth',
            author=user,
            text='yesterday_10',
            added_at=timezone.now() - datetime.timedelta(days=1),
            rating=10
        )
        Answer.objects.create(
            text='answer',
            author=testuser,
            question=question
        )

    def check_trending(self, response):
        trending_list_questions = Question.objects.popular()
        self.assertQuerysetEqual(response.context['trending'], map(repr, trending_list_questions))

    def check_templates(self, response, list_temp):
        templates = [i.name for i in response.templates]
        for i in list_temp:
            self.assertIn(i, templates)

    def test_get_another_user(self):
        response = self.client.get(reverse('users:profile', args=[User.objects.get(username='testuser').id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['user'], AnonymousUser)
        self.assertEqual(response.context['error'], 'Sorry!\nYou can watch only your profile page')
        self.check_templates(response, ['users/profile.html', 'base.html'])
        self.check_trending(response)

    def test_get(self):
        self.client.login(username='testuser', password='testuser123')
        response = self.client.get(reverse('users:profile', args=[User.objects.get(username='testuser').id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], User.objects.get(username='testuser'))
        self.assertEqual(response.context['error'], '')
        self.check_templates(response, ['users/profile.html', 'base.html'])
        self.check_trending(response)

    def test_post(self):
        question = Question.objects.get(title='first')
        answer = Answer.objects.get(text='answer')
        user = User.objects.get(username='testuser')
        user.userprofile.vote_question(question.id, 1, question.title)
        user.userprofile.vote_answer(answer.id, 1, answer.question.title, answer.question.id)
        self.client.login(username='testuser', password='testuser123')
        response = self.client.post(reverse('users:profile', args=[user.id]), data={'change_choice': 'Change question'})
        user = User.objects.get(username='testuser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)
        self.assertIsNone(user.userprofile.id_voted_question)
        self.assertIsNone(user.userprofile.value_voted_question)
        self.assertIsNone(user.userprofile.title_voted_question)
        self.check_templates(response, ['users/profile.html', 'base.html'])
        self.check_trending(response)
        response = self.client.post(reverse('users:profile', args=[user.id]), data={'change_choice': 'Change answer'})
        user = User.objects.get(username='testuser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)
        self.assertIsNone(user.userprofile.id_voted_answer)
        self.assertIsNone(user.userprofile.value_voted_answer)
        self.assertIsNone(user.userprofile.title_voted_answer)
        self.assertIsNone(user.userprofile.id_question_voted_answer)
        self.check_templates(response, ['users/profile.html', 'base.html'])
        self.check_trending(response)


class EditProfileViewTest(TestCase):
    def setUp(self):
        testuser = User.objects.create(username='testuser')
        testuser.set_password('testuser123')
        testuser.save()
        UserProfile.objects.create(user=testuser)
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

    def check_templates(self, response, list_temp):
        templates = [i.name for i in response.templates]
        for i in list_temp:
            self.assertIn(i, templates)

    def test_get(self):
        self.client.login(username='testuser', password='testuser123')
        response = self.client.get(reverse('users:edit_profile', args=[User.objects.get(username='testuser').id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['new_fields_form'], ChangeFieldsForm)
        self.check_templates(response, ['users/edit_profile.html', 'base.html'])
        self.check_trending(response)

    def test_post_bad(self):
        self.client.login(username='testuser', password='testuser123')
        response = self.client.post(reverse('users:edit_profile', args=[User.objects.get(username='testuser').id]),
                                    data={'new_email': 'django'})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['new_fields_form'], ChangeFieldsForm)
        self.check_templates(response, ['users/edit_profile.html', 'base.html'])
        self.check_trending(response)

    def test_post_ok(self):
        self.client.login(username='testuser', password='testuser123')
        response = self.client.post(reverse('users:edit_profile', args=[User.objects.get(username='testuser').id]),
                                    data={'new_email': 'new_mail@mail.ru'},
                                    follow=True)
        user = User.objects.get(username='testuser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.email, 'new_mail@mail.ru')
        self.assertEqual(response.redirect_chain, [(reverse('users:profile', args=[user.id]), 302)])
        self.check_templates(response, ['users/profile.html', 'base.html'])
        self.check_trending(response)