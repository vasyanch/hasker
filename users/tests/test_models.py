import os
import tempfile
from django.test import TestCase, override_settings
from django.utils import timezone

from PIL import Image

from qa.models import Question, Answer
from users.models import User, UserProfile, user_directory_path


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new('RGB', size, color)
    image.save(temp_file, 'jpeg')
    return temp_file


class UserProfileTest(TestCase):

    def setUp(self):
        self.testuser = User.objects.create(username='testuser')
        self.testuser.set_password('testusert123')
        self.testuser.save()
        self.question = Question.objects.create(title='test', text='test question', author=self.testuser)
        self.answer = Answer.objects.create(text='test', author=self.testuser, question=self.question)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_ava(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        test_image = get_temporary_image(temp_file)
        testuser = User.objects.create(username='avauser')
        testuser.userprofile.avatar = test_image.name
        testuser.save()
        self.assertEqual(testuser.userprofile.avatar.url, testuser.userprofile.get_url_avatar())

    def test_user_directory_path(self):
        id = self.testuser.id
        path_ava = user_directory_path(self.testuser.userprofile, 'testava')
        self.assertEqual(path_ava, os.path.join('ava_user_{}'.format(id), 'testava'))

    def test_get_url_avata_no_ava(self):
        url = self.testuser.userprofile.get_url_avatar()
        self.assertEqual(url, '/static/users/images/no_ava.jpg')

    def test_get_date_joined(self):
        date = self.testuser.userprofile.get_date_joined()
        self.assertEqual(date, timezone.now().strftime('%d.%m.%Y'))

    def test_get_url(self):
        url = self.testuser.userprofile.get_url()
        self.assertEqual(url, '/users/profile/{}/'.format(self.testuser.id))

    def test_vote_question(self):
        self.testuser.userprofile.vote_question(self.question.id, -1, self.question.title)
        self.assertEqual(self.testuser.userprofile.id_voted_question, self.question.id)
        self.assertEqual(self.testuser.userprofile.value_voted_question, -1)
        self.assertEqual(self.testuser.userprofile.title_voted_question, self.question.title)
        self.assertEqual(self.testuser.userprofile.get_url_voted_question(),
                         '/qa/question/{}/'.format(self.question.id))

    def test_cancel_vote_question(self):
        self.testuser.userprofile.vote_question(self.question.id, -1, self.question.title)
        self.testuser.userprofile.cancel_vote_question()
        self.assertIsNone(self.testuser.userprofile.id_voted_question)
        self.assertIsNone(self.testuser.userprofile.value_voted_question)
        self.assertIsNone(self.testuser.userprofile.title_voted_question)

    def test_vote_answer(self):
        self.testuser.userprofile.vote_answer(self.answer.id, 1, self.question.title, self.question.id)
        self.assertEqual(self.testuser.userprofile.id_voted_answer, self.answer.id)
        self.assertEqual(self.testuser.userprofile.value_voted_answer, 1)
        self.assertEqual(self.testuser.userprofile.title_voted_answer, self.question.title)
        self.assertEqual(self.testuser.userprofile.id_question_voted_answer, self.question.id)
        self.assertEqual(self.testuser.userprofile.get_url_voted_answer(), '/qa/question/{}/'.format(self.question.id))

    def test_cancel_vote_answer(self):
        self.testuser.userprofile.vote_answer(self.answer.id, 1, self.question.title, self.question.id)
        self.testuser.userprofile.cancel_vote_answer()
        self.assertIsNone(self.testuser.userprofile.id_voted_answer)
        self.assertIsNone(self.testuser.userprofile.value_voted_answer)
        self.assertIsNone(self.testuser.userprofile.title_voted_answer)
        self.assertIsNone(self.testuser.userprofile.id_question_voted_answer)


