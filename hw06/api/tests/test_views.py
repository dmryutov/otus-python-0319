from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.serializers import QuestionSerializer
from question.models import Answer, Question, Tag, Vote
from user.models import User


class QuestionTestCaseBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        # Create users
        cls.user1 = User.objects.create_user('user1', 'user1@mail.com', 'password12345')
        # Create questions
        cls.question1 = Question.objects.create(user=cls.user1, title='Title 1', text='text 1')
        cls.question2 = Question.objects.create(user=cls.user1, title='Title 2', text='text 2')
        # Create answers
        cls.answer1 = Answer.objects.create(question=cls.question1, user=cls.user1, text='text 1')
        cls.answer2 = Answer.objects.create(question=cls.question1, user=cls.user1, text='text 2')
        cls.answer3 = Answer.objects.create(question=cls.question2, user=cls.user1, text='text 3')
        # Create votes
        vote1 = Vote.objects.create(user=cls.user1, value=True)
        vote2 = Vote.objects.create(user=cls.user1, value=False)
        cls.question1.votes.set([vote1])
        cls.answer1.votes.set([vote2])
        # Create tags
        tag1 = Tag.objects.create(name='tag1')
        cls.question1.tags.set([tag1])


class QuestionListViewTestCase(QuestionTestCaseBase):
    def test_authorized_user(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('api_question_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_not_authorized(self):
        response = self.client.get(reverse('api_question_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)


class TrendingListViewTestCase(QuestionTestCaseBase):
    def test_authorized_user(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('api_trending_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['id'], self.question1.id)

    def test_not_authorized(self):
        response = self.client.get(reverse('api_trending_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.question1.id)


class SearchListViewViewTestCase(QuestionTestCaseBase):
    def test_search(self):
        self.client.force_authenticate(user=self.user1)

        search_query = 'tle 1'
        response = self.client.get(reverse('api_search_list'), {'q': search_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_empty_search_query(self):
        self.client.force_authenticate(user=self.user1)

        search_query = ''
        response = self.client.get(reverse('api_search_list'), {'q': search_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_no_matches(self):
        self.client.force_authenticate(user=self.user1)

        search_query = 'no-question'
        response = self.client.get(reverse('api_search_list'), {'q': search_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_not_authorized(self):
        search_query = 'ext 1'
        response = self.client.get(reverse('api_search_list'), {'q': search_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class QuestionDetailViewTestCase(QuestionTestCaseBase):
    def test_authorized_user(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('api_question_detail', kwargs={'pk': self.question1.id}))
        serializer_data = QuestionSerializer(instance=self.question1).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_not_authorized(self):
        response = self.client.get(reverse('api_question_detail', kwargs={'pk': self.question1.id}))
        serializer_data = QuestionSerializer(instance=self.question1).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)


class AnswerListViewTestCase(QuestionTestCaseBase):
    def test_authorized_user(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('api_answer_list', kwargs={'pk': self.question1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['id'], self.answer2.id)

    def test_not_authorized(self):
        response = self.client.get(reverse('api_answer_list', kwargs={'pk': self.question1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['id'], self.answer2.id)
