from django.test import TestCase
from authapp.models import User
from django.urls import reverse
from http import HTTPStatus
from django.contrib.messages import get_messages


class AuthTest(TestCase):

    def setUp(self) -> None:
        super().setUp()
        User.objects.create_superuser(username='django', email='django@django.com', password='django')

    def test_login_with_username(self):
        url = reverse('auth:login')
        result = self.client.post(url, {'username': 'django', 'password': 'django'})
        self.assertEqual(result.status_code, HTTPStatus.FOUND)

    def test_login_with_email(self):
        url = reverse('auth:login')
        result = self.client.post(url, {'username': 'django@django.com', 'password': 'django'})
        self.assertEqual(result.status_code, HTTPStatus.FOUND)

    def test_login_with_wrong_data(self):
        url = reverse('auth:login')
        result = self.client.post(url, {'username': 'Some user', 'password': 'django'})
        messages = list(get_messages(result.wsgi_request))
        self.assertEqual(str(messages[0]), "Неправильное имя пользователя или пароль!")

    def test_create_new_user(self):
        url = reverse('auth:register')
        result = self.client.post(url, {
            'username': 'django2',
            'password1': 'Passwd123',
            'password2': 'Passwd123',
            'first_name': 'Name',
            'last_name': 'Somename',
            'email': 'django15@gmail.com'
        })
        self.assertEqual(result.status_code, HTTPStatus.FOUND)
        self.assertEqual(User.objects.all().count(), 2)
