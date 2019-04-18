from django.test import TestCase

from question.models import Question, Tag, Vote
from user.models import User


class TagTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')

    def setUp(self):
        self.tag = Tag.objects.create(name='Tag 1')

    def test_model_str(self):
        self.assertEqual(str(self.tag), 'Tag 1')


class QuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')

    def setUp(self):
        self.question = Question.objects.create(user=self.user, title='Title 1', text='text 1')

    def test_model_str(self):
        self.assertEqual(str(self.question), 'Title 1')


class QAManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')

    def setUp(self):
        self.question = Question.objects.create(user=self.user, title='Title 1', text='text 1')
        vote1 = Vote.objects.create(user=self.user, value=True)
        vote2 = Vote.objects.create(user=self.user, value=False)
        vote3 = Vote.objects.create(user=self.user, value=False)
        self.question.votes.set([vote1, vote2, vote3])

    def test_load_rating(self):
        question = Question.objects.load_rating().first()
        self.assertEqual(question.rating, -1)
