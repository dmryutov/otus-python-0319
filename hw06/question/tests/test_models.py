from django.test import TestCase

from question.models import Answer, Question, Tag, Vote
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

    def test_get_answers(self):
        # Create questions
        answer1 = Answer.objects.create(question=self.question, user=self.user, text='text 1')
        answer2 = Answer.objects.create(question=self.question, user=self.user, text='text 2')
        self.question.answers.set([answer1, answer2])

        answers = self.question.get_answers()
        self.assertEqual(len(answers), 2)
        self.assertEqual(answers[0].id, answer2.id)

    def test_get_tag_names(self):
        # Create tags
        tag1 = Tag.objects.create(name='tag1')
        tag2 = Tag.objects.create(name='tag2')
        self.question.tags.set([tag1, tag2])

        tags = self.question.get_tag_names()
        self.assertEqual(tags, ['tag1', 'tag2'])


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
