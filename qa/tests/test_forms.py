from django.test import TestCase
from qa.forms import AskForm, AnswerForm
from qa.models import Question, Answer, Tag
from users.models import User, UserProfile


class AskFormTest(TestCase):
    def setUp(self):
        self.testuser = User.objects.create(username='testuser')
        self.testuser.set_password('testuser123')
        self.testuser.save()

    def test_AskForm(self):
        form = AskForm(self.testuser, data={'title': 'django', 'text': 'test form', 'tags': 'django,test,python'})
        self.assertTrue(form.is_valid())
        new_question = form.save()
        self.assertIsInstance(new_question, Question)
        self.assertQuerysetEqual(new_question.get_tags(),
                                 map(repr, Tag.objects.filter(questions=new_question.id)),
                                 ordered=False)
        form_error = AskForm(self.testuser, data={'title': 'd'*101, 'text': 'test form', 'tags': 'django,test,python'})
        self.assertFalse(form_error.is_valid())


class AnswerFormTest(TestCase):
    def setUp(self):
        self.testuser = User.objects.create(username='testuser')
        self.testuser.set_password('testuser123')
        self.testuser.save()
        self.question = Question.objects.create(title='for answer', author=self.testuser)

    def test_AnswerForm(self):
        id = self.question.id
        form = AnswerForm(self.testuser, data={'text': 'new answer', 'question': '{}'.format(id)})
        self.assertTrue(form.is_valid())
        new_answer = form.save()
        self.assertIsInstance(new_answer, Answer)
        self.assertEqual(new_answer.question_id, id)
        form_error = AnswerForm(self.testuser, data={'text': 'new answer', 'question': 10})
        self.assertRaises(Question.DoesNotExist, form_error.is_valid)
