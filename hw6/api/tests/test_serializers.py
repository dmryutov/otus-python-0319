from rest_framework.test import APITestCase, APIClient

from api.serializers import AnswerSerializer, QuestionSerializer, VoteSerializer
from question.models import Answer, Question, Vote
from user.models import User


class VoteSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')
        cls.vote = Vote.objects.create(user=cls.user, value=True)

        # Create request
        cls.request = APIClient().request()
        cls.request.user = cls.user

    def test_contains_expected_fields(self):
        serializer = VoteSerializer(instance=self.vote, context={'request': self.request})
        expected_keys = ['user', 'value']
        self.assertCountEqual(serializer.data.keys(), expected_keys)


class QuestionSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')
        cls.question = Question.objects.create(user=cls.user, title='Title 1', text='text')

        # Create request
        cls.request = APIClient().request()
        cls.request.user = cls.user

    def test_contains_expected_fields(self):
        serializer = QuestionSerializer(instance=self.question, context={'request': self.request})
        expected_keys = ['id', 'user', 'tags', 'votes', 'title', 'text', 'created']
        self.assertCountEqual(serializer.data.keys(), expected_keys)


class AnswerSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')
        cls.question = Question.objects.create(user=cls.user, title='Title 1', text='text')
        cls.answer = Answer.objects.create(user=cls.user, question=cls.question, text='text')

        # Create request
        cls.request = APIClient().request()
        cls.request.user = cls.user

    def test_contains_expected_fields(self):
        serializer = AnswerSerializer(instance=self.answer, context={'request': self.request})
        expected_keys = ['id', 'user', 'votes', 'created', 'text']
        self.assertCountEqual(serializer.data.keys(), expected_keys)
