import os

from django.test import TestCase
from django.urls import reverse

from user.models import User


class SignUpViewTestCase(TestCase):
    def test_create_user(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user1',
            'email': 'user1@mail.com',
            'password1': 'Pswrddd555',
            'password2': 'Pswrddd555',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 302)

    def test_upload_avatar(self):
        with open('test_data/avatar.png', 'rb') as f:
            response = self.client.post(reverse('signup'), {
                'username': 'user1',
                'email': 'user1@mail.com',
                'password1': 'Pswrddd555',
                'password2': 'Pswrddd555',
                'avatar': f,
            })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(os.path.isfile('media/user/avatar.png'))
        os.remove('media/user/avatar.png')

    def test_empty_login(self):
        response = self.client.post(reverse('signup'), {
            'email': 'user1@mail.com',
            'password1': 'Pswrddd555',
            'password2': 'Pswrddd555',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_empty_password(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user1',
            'email': 'user1@mail.com',
            'password2': 'Pswrddd555',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_passwords_not_equal(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user1',
            'email': 'user1@mail.com',
            'password1': 'Pswrddd555',
            'password2': '54321password',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn&#39;t match')


class SettingsViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user = User.objects.create_user('user1', 'user1@mail.com', 'password12345')

    def test_update_settings(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('user_settings'), {
            'email': 'user1@mail.com',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 302)

    def test_upload_avatar(self):
        self.client.force_login(user=self.user)

        with open('test_data/avatar.png', 'rb') as f:
            response = self.client.post(reverse('user_settings'), {
                'email': 'user1@mail.com',
                'avatar': f,
            })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(os.path.isfile('media/user/avatar.png'))
        os.remove('media/user/avatar.png')

    def test_invalid_email(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('user_settings'), {
            'email': 'invalid',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address')

    def test_not_authorized(self):
        response = self.client.post(reverse('user_settings'), {
            'email': 'user1@mail.com',
            'avatar': None,
        })
        self.assertEqual(response.status_code, 302)
