from django.test import TestCase
from django.urls import reverse

from question.models import Answer, Question, Tag, Vote
from user.models import User


class QuestionTestCaseBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user1 = User.objects.create_user('user1', 'user1@mail.com', 'password12345')
        cls.user2 = User.objects.create_user('user2', 'user2@mail.com', 'password12345')
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
    def test_question_list(self):
        self.client.force_login(user=self.user1)

        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)

    def test_question_hot(self):
        self.client.force_login(user=self.user1)

        response = self.client.get(reverse('question_hot'))
        self.assertEqual(response.status_code, 200)

    def test_not_authorized(self):
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)


class SearchViewTestCase(QuestionTestCaseBase):
    def test_search(self):
        self.client.force_login(user=self.user1)

        search_query = 'tle 1'
        response = self.client.get(reverse('question_search'), {'q': search_query})
        self.assertEqual(response.status_code, 200)

    def test_empty_search_query(self):
        self.client.force_login(user=self.user1)

        search_query = ''
        response = self.client.get(reverse('question_search'), {'q': search_query})
        self.assertEqual(response.status_code, 200)

    def test_no_matches(self):
        self.client.force_login(user=self.user1)

        search_query = 'no-question'
        response = self.client.get(reverse('question_search'), {'q': search_query})
        self.assertEqual(response.status_code, 200)

    def test_tag_prefix(self):
        self.client.force_login(user=self.user1)

        search_query = 'tag:tag1'
        response = self.client.get(reverse('question_search'), {'q': search_query})
        self.assertEqual(response.status_code, 302)


class TagViewTestCase(QuestionTestCaseBase):
    def test_search(self):
        self.client.force_login(user=self.user1)

        tag_name = 'tag1'
        response = self.client.get(reverse('tag_detail', kwargs={'name': tag_name}))
        self.assertEqual(response.status_code, 200)

    def test_no_matches(self):
        self.client.force_login(user=self.user1)

        tag_name = 'no-tag'
        response = self.client.get(reverse('tag_detail', kwargs={'name': tag_name}))
        self.assertEqual(response.status_code, 200)


class QuestionAddViewTestCase(QuestionTestCaseBase):
    def test_add_question(self):
        self.client.force_login(user=self.user1)

        response = self.client.post(reverse('question_add'), {
            'title': 'Title 3',
            'text': 'text 3',
            'tags': [],
        })
        self.assertEqual(response.status_code, 302)

    def test_not_authorized(self):
        response = self.client.post(reverse('question_add'), {
            'title': 'Title 3',
            'text': 'text 3',
            'tags': [],
        })
        self.assertEqual(response.status_code, 302)


class AnswerAcceptViewTestCase(QuestionTestCaseBase):
    def test_accept_answer(self):
        self.client.force_login(user=self.user1)

        response = self.client.post(reverse('accept_answer', kwargs={'pk': self.answer1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_not_authorized(self):
        response = self.client.post(reverse('accept_answer', kwargs={'pk': self.answer1.pk}))
        self.assertEqual(response.status_code, 302)


class VoteViewTestCase(QuestionTestCaseBase):
    def test_new_vote(self):
        self.client.force_login(user=self.user2)

        response = self.client.post(reverse('vote'), {
            'id': self.question1.id,
            'object': 'question',
            'value': 'up',
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_vote(self):
        self.client.force_login(user=self.user2)
        vote = Vote.objects.create(user=self.user2, value=True)
        self.question2.votes.set([vote])

        response = self.client.post(reverse('vote'), {
            'id': self.question2.id,
            'object': 'question',
            'value': 'up',
        })
        self.assertEqual(response.status_code, 200)

    def test_change_vote(self):
        self.client.force_login(user=self.user2)
        vote = Vote.objects.create(user=self.user2, value=True)
        self.question2.votes.set([vote])

        response = self.client.post(reverse('vote'), {
            'id': self.question2.id,
            'object': 'question',
            'value': 'down',
        })
        self.assertEqual(response.status_code, 200)

    def test_invalid_object_type(self):
        self.client.force_login(user=self.user2)

        response = self.client.post(reverse('vote'), {
            'id': self.question1.id,
            'object': 'invalid',
            'value': 'up',
        })
        self.assertEqual(response.status_code, 400)

    def test_current_user_is_author(self):
        self.client.force_login(user=self.user1)

        response = self.client.post(reverse('vote'), {
            'id': self.question1.id,
            'object': 'question',
            'value': 'up',
        })
        self.assertEqual(response.status_code, 403)

    def test_not_authorized(self):
        response = self.client.post(reverse('vote'), {
            'id': self.question1.id,
            'object': 'question',
            'value': 'up',
        })
        self.assertEqual(response.status_code, 302)
