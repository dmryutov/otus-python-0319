from django.test import TestCase
from django.urls import reverse


class SignUpViewTestCase(TestCase):
    def test_create_user(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user1',
            'email': 'user1@mail.com',
            'password1': 'password12345',
            'password2': 'password12345',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 200)
