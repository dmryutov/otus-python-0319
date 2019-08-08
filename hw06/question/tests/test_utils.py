from unittest.mock import patch

from django.test import client, TestCase
from django.urls import reverse

from question.models import Answer, Question
from question.utils import send_email_notification
from user.models import User


class SendEmailNotificationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')
        # Create question
        cls.question = Question.objects.create(user=cls.user, title='Title 1', text='text 1')
        # Create answer
        cls.answer = Answer.objects.create(question=cls.question, user=cls.user, text='text 1')
        # Create request
        cls.request = client.RequestFactory().get(reverse('question_list'))

    @patch('question.utils.send_mail')
    def test_send_notification(self, mock_send_mail):
        self.assertIsNone(send_email_notification(self.request, self.question, self.answer))
        self.assertEqual(len(mock_send_mail.call_args[0]), 4)
        self.assertIn('html_message', mock_send_mail.call_args[1])
